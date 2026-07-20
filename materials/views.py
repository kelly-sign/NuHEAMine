from rest_framework import viewsets, filters, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.db import transaction
import pandas as pd
import io
from io import BytesIO
from datetime import datetime
from .models import Material, Process, RoomTempProperty, HTProperty, ImpTest, CreTest, FatTest, IrrCondition, MicrostructureEvolution, Embrittlement, IrrCreep, Document, Hardening
from .serializers import (
    MaterialSerializer, MaterialSearchSerializer, MaterialRangeQuerySerializer,
    MaterialMultiConditionSerializer, MaterialExportSerializer, MaterialImportSerializer,
    MaterialBatchDeleteSerializer, ProcessSerializer, RoomTempPropertySerializer,
    HTPropertySerializer, ImpTestSerializer, CreTestSerializer, FatTestSerializer,
    IrrConditionSerializer, MicrostructureEvolutionSerializer, EmbrittlementSerializer,
    IrrCreepSerializer, DocumentSerializer, HardeningSerializer
)
from django.http import HttpResponse
import logging
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework import serializers
from django.utils import timezone
import math
import os

logger = logging.getLogger(__name__)

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class MaterialViewSet(viewsets.ModelViewSet):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['material_id', 'material_name']
    search_fields = ['material_name', 'material_id']
    ordering_fields = ['entry_time', 'modify_time']

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # 获取搜索参数
        search_query = self.request.query_params.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(material_name__icontains=search_query) |
                Q(material_id__icontains=search_query)
            )
        
        # 元素成分范围过滤
        composition_filters = {}
        elements = [
            'al', 'c', 'co', 'cr', 'cu', 'fe', 'hf', 'mg', 'mn', 'mo',
            'n', 'nb', 'ni', 'sc', 'si', 'sn', 'ta', 'ti', 'v', 'w',
            'y', 'zn', 'zr'
        ]
        
        for element in elements:
            min_val = self.request.query_params.get(f'composition_{element}_min')
            max_val = self.request.query_params.get(f'composition_{element}_max')
            if min_val is not None:
                composition_filters[f'composition_{element}__gte'] = float(min_val)
            if max_val is not None:
                composition_filters[f'composition_{element}__lte'] = float(max_val)

        # 时间范围过滤
        entry_time_start = self.request.query_params.get('entry_time_start')
        entry_time_end = self.request.query_params.get('entry_time_end')
        if entry_time_start:
            queryset = queryset.filter(entry_time__gte=entry_time_start)
        if entry_time_end:
            queryset = queryset.filter(entry_time__lte=entry_time_end)

        return queryset.filter(Q(**composition_filters))

    def create(self, request, *args, **kwargs):
        """创建新材料"""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except serializers.ValidationError as e:
            # 处理验证错误
            error_message = str(e.detail)
            if isinstance(e.detail, dict):
                # 如果是字典类型的错误，提取第一个错误消息
                for field, errors in e.detail.items():
                    if isinstance(errors, list):
                        error_message = errors[0]
                    else:
                        error_message = str(errors)
                    break
            return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"创建材料时发生错误: {str(e)}")
            return Response(
                {'error': f'创建失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def update(self, request, *args, **kwargs):
        """更新材料数据"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """删除材料数据"""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'])
    def batch_delete(self, request):
        """批量删除材料数据"""
        serializer = MaterialBatchDeleteSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        material_ids = serializer.validated_data['material_ids']
        with transaction.atomic():
            deleted_count = Material.objects.filter(material_id__in=material_ids).delete()[0]
        
        return Response({
            'message': f'成功删除 {deleted_count} 条材料数据',
            'deleted_count': deleted_count
        })

    @action(detail=False, methods=['post'])
    def import_data(self, request):
        """导入材料数据"""
        try:
            # 检查是否有文件上传
            if 'file' not in request.FILES:
                return Response({
                    'error': '请选择要导入的Excel文件',
                    'success': False
                }, status=status.HTTP_400_BAD_REQUEST)

            file = request.FILES['file']
            
            # 检查文件类型
            if not file.name.endswith(('.xlsx', '.xls')):
                return Response({
                    'error': '只支持 Excel 文件格式 (.xlsx, .xls)',
                    'success': False
                }, status=status.HTTP_400_BAD_REQUEST)

            # 检查文件大小
            if file.size > 10 * 1024 * 1024:  # 10MB
                return Response({
                    'error': '文件大小不能超过10MB',
                    'success': False
                }, status=status.HTTP_400_BAD_REQUEST)

            try:
                # 尝试读取Excel文件
                df = pd.read_excel(
                    file,
                    engine='openpyxl',  # 使用 openpyxl 引擎
                    dtype={
                        'material_name': str,
                        'composition_al': float,
                        'composition_c': float,
                        'composition_co': float,
                        'composition_cr': float,
                        'composition_cu': float,
                        'composition_fe': float,
                        'composition_hf': float,
                        'composition_mg': float,
                        'composition_mn': float,
                        'composition_mo': float,
                        'composition_n': float,
                        'composition_nb': float,
                        'composition_ni': float,
                        'composition_sc': float,
                        'composition_si': float,
                        'composition_sn': float,
                        'composition_ta': float,
                        'composition_ti': float,
                        'composition_v': float,
                        'composition_w': float,
                        'composition_y': float,
                        'composition_zn': float,
                        'composition_zr': float
                    }
                )
            except Exception as e:
                logger.error(f"Excel文件读取失败: {str(e)}")
                return Response({
                    'error': f'Excel文件读取失败: {str(e)}',
                    'success': False,
                    'detail': '请确保Excel文件格式正确，且包含必要的列'
                }, status=status.HTTP_400_BAD_REQUEST)

            # 验证必需列
            required_columns = ['material_name']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                return Response({
                    'error': f'Excel文件缺少必需列: {", ".join(missing_columns)}',
                    'success': False
                }, status=status.HTTP_400_BAD_REQUEST)

            # 验证元素列
            element_columns = [
                'composition_al', 'composition_c', 'composition_co', 'composition_cr',
                'composition_cu', 'composition_fe', 'composition_hf', 'composition_mg',
                'composition_mn', 'composition_mo', 'composition_n', 'composition_nb',
                'composition_ni', 'composition_sc', 'composition_si', 'composition_sn',
                'composition_ta', 'composition_ti', 'composition_v', 'composition_w',
                'composition_y', 'composition_zn', 'composition_zr'
            ]
            
            # 检查是否至少有一个元素列
            available_element_columns = [col for col in element_columns if col in df.columns]
            if not available_element_columns:
                return Response({
                    'error': 'Excel文件必须包含至少一个元素成分列',
                    'success': False
                }, status=status.HTTP_400_BAD_REQUEST)

            total_count = len(df)
            success_count = 0
            error_count = 0
            errors = []

            # 使用事务确保数据一致性
            with transaction.atomic():
                # 获取所有已存在的材料名称
                existing_materials = set(Material.objects.values_list('material_name', flat=True))
                
                for index, row in df.iterrows():
                    try:
                        # 准备材料数据
                        material_name = str(row['material_name']).strip()
                        if pd.isna(material_name) or material_name == '':
                            error_count += 1
                            errors.append({
                                'row': index + 2,
                                'error': '材料名称不能为空'
                            })
                            continue

                        material_data = {
                            'material_name': material_name
                        }

                        # 检查材料名称是否已存在
                        if material_name in existing_materials:
                            error_count += 1
                            errors.append({
                                'row': index + 2,
                                'error': f'材料名称 "{material_name}" 已存在'
                            })
                            continue

                        # 处理元素成分
                        total_composition = 0
                        for col in available_element_columns:
                            try:
                                value = float(row[col]) if pd.notna(row[col]) else 0
                                if value < 0:
                                    error_count += 1
                                    errors.append({
                                        'row': index + 2,
                                        'error': f'元素 {col.replace("composition_", "").upper()} 含量不能为负数'
                                    })
                                    continue
                                material_data[col] = value
                                total_composition += value
                            except (ValueError, TypeError) as e:
                                error_count += 1
                                errors.append({
                                    'row': index + 2,
                                    'error': f'元素 {col.replace("composition_", "").upper()} 含量格式错误'
                                })
                                continue

                        # 检查元素总含量
                        # 由于Excel读取与浮点计算可能带来精度误差，允许总和在四舍五入到2位后仍不超过100
                        total_composition_rounded = round(total_composition, 2)
                        if total_composition_rounded > 100:
                            error_count += 1
                            errors.append({
                                'row': index + 2,
                                'error': f'元素总含量 ({total_composition_rounded:.2f}%) 超过100%'
                            })
                            continue

                        # 创建材料记录
                        material_serializer = MaterialSerializer(data=material_data)
                        if material_serializer.is_valid():
                            material = material_serializer.save()
                            existing_materials.add(material_name)
                            success_count += 1
                        else:
                            error_count += 1
                            error_msg = '数据验证失败: '
                            for field, field_errors in material_serializer.errors.items():
                                error_msg += f"{field}: {field_errors[0]}; "
                            errors.append({
                                'row': index + 2,
                                'error': error_msg.strip('; ')
                            })

                    except Exception as e:
                        error_count += 1
                        errors.append({
                            'row': index + 2,
                            'error': f'处理数据时出错: {str(e)}'
                        })
                        logger.error(f"处理第{index + 2}行数据时出错: {str(e)}")

            response_data = {
                'success': error_count == 0,
                'message': f'导入完成：共{total_count}条数据，成功{success_count}条，失败{error_count}条',
                'total_count': total_count,
                'success_count': success_count,
                'error_count': error_count,
                'errors': errors[:10]  # 只返回前10个错误
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"导入材料数据失败: {str(e)}")
            return Response({
                'error': f'导入失败: {str(e)}',
                'success': False,
                'detail': '请检查Excel文件格式是否正确，并确保包含必要的列和数据'
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def keyword_search(self, request):
        """关键词搜索"""
        serializer = MaterialSearchSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        keyword = serializer.validated_data.get('keyword', '')
        elements = serializer.validated_data.get('elements', [])
        page = serializer.validated_data.get('page', 1)
        page_size = serializer.validated_data.get('page_size', 10)

        queryset = self.get_queryset()
        
        # 构建查询条件
        conditions = Q()
        if keyword:
            conditions |= Q(material_name__icontains=keyword)
        
        for element in elements:
            element_field = f'composition_{element.lower()}'
            if hasattr(Material, element_field):
                conditions |= Q(**{f'{element_field}__gt': 0})

        queryset = queryset.filter(conditions)
        
        # 分页
        start = (page - 1) * page_size
        end = start + page_size
        total_count = queryset.count()
        queryset = queryset[start:end]
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'results': serializer.data,
            'total': total_count,
            'page': page,
            'page_size': page_size,
            'total_pages': (total_count + page_size - 1) // page_size
        })

    @action(detail=False, methods=['post'])
    def range_query(self, request):
        """范围查询"""
        serializer = MaterialRangeQuerySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        element = serializer.validated_data['element'].lower()
        min_value = serializer.validated_data['min_value']
        max_value = serializer.validated_data['max_value']
        page = serializer.validated_data.get('page', 1)
        page_size = serializer.validated_data.get('page_size', 10)

        element_field = f'composition_{element}'
        if not hasattr(Material, element_field):
            return Response(
                {'error': f'不支持的元素的元素: {element}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        queryset = self.get_queryset().filter(
            **{
                f'{element_field}__gte': min_value,
                f'{element_field}__lte': max_value
            }
        )
        
        # 分页
        start = (page - 1) * page_size
        end = start + page_size
        total_count = queryset.count()
        queryset = queryset[start:end]
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'results': serializer.data,
            'total': total_count,
            'page': page,
            'page_size': page_size,
            'total_pages': (total_count + page_size - 1) // page_size
        })

    @action(detail=False, methods=['post'])
    def multi_condition_query(self, request):
        """多条件查询"""
        serializer = MaterialMultiConditionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        conditions = serializer.validated_data['conditions']
        page = serializer.validated_data.get('page', 1)
        page_size = serializer.validated_data.get('page_size', 10)
        queryset = self.get_queryset()

        for condition in conditions:
            element = condition['element'].lower()
            element_field = f'composition_{element}'
            if not hasattr(Material, element_field):
                return Response(
                    {'error': f'不支持的元素的元素: {element}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            queryset = queryset.filter(
                **{
                    f'{element_field}__gte': condition['min_value'],
                    f'{element_field}__lte': condition['max_value']
                }
            )
        
        # 分页
        start = (page - 1) * page_size
        end = start + page_size
        total_count = queryset.count()
        queryset = queryset[start:end]
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'results': serializer.data,
            'total': total_count,
            'page': page,
            'page_size': page_size,
            'total_pages': (total_count + page_size - 1) // page_size
        })

    @action(detail=False, methods=['post'])
    def export_results(self, request):
        """导出查询结果"""
        serializer = MaterialExportSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        results = serializer.validated_data['search_results']
        format_type = serializer.validated_data['format']

        if format_type == 'excel':
            # 创建DataFrame
            df = pd.DataFrame(results)
            
            # 创建Excel文件
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Materials')
                
                # 获取工作表
                worksheet = writer.sheets['Materials']
                
                # 调整列宽
                for idx, col in enumerate(df.columns):
                    max_length = max(
                        df[col].astype(str).apply(len).max(),
                        len(str(col))
                    )
                    worksheet.set_column(idx, idx, max_length + 2)

            output.seek(0)
            
            # 生成文件名
            filename = f'materials_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
            
            return Response(
                {
                    'file': output.getvalue(),
                    'filename': filename
                },
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

    @action(detail=False, methods=['post'])
    def export_data(self, request):
        """导出材料数据"""
        try:
            from django.utils import timezone
            
            format_type = request.data.get('format', 'excel')
            material_ids = request.data.get('material_ids', [])
            
            # 获取要导出的材料数据
            queryset = self.get_queryset()
            if material_ids:
                queryset = queryset.filter(id__in=material_ids)
            
            # 准备导出数据
            export_data = []
            for material in queryset:
                # 转换时间为本地时区
                entry_time = timezone.localtime(material.entry_time) if material.entry_time.tzinfo else timezone.localtime(timezone.make_aware(material.entry_time))
                modify_time = timezone.localtime(material.modify_time) if material.modify_time.tzinfo else timezone.localtime(timezone.make_aware(material.modify_time))
                
                material_data = {
                    'material_name': material.material_name,
                    'composition_al': material.composition_al,
                    'composition_c': material.composition_c,
                    'composition_co': material.composition_co,
                    'composition_cr': material.composition_cr,
                    'composition_cu': material.composition_cu,
                    'composition_fe': material.composition_fe,
                    'composition_hf': material.composition_hf,
                    'composition_mg': material.composition_mg,
                    'composition_mn': material.composition_mn,
                    'composition_mo': material.composition_mo,
                    'composition_n': material.composition_n,
                    'composition_nb': material.composition_nb,
                    'composition_ni': material.composition_ni,
                    'composition_sc': material.composition_sc,
                    'composition_si': material.composition_si,
                    'composition_sn': material.composition_sn,
                    'composition_ta': material.composition_ta,
                    'composition_ti': material.composition_ti,
                    'composition_v': material.composition_v,
                    'composition_w': material.composition_w,
                    'composition_y': material.composition_y,
                    'composition_zn': material.composition_zn,
                    'composition_zr': material.composition_zr,
                    'entry_time': entry_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'modify_time': modify_time.strftime('%Y-%m-%d %H:%M:%S')
                }
                export_data.append(material_data)
            
            # 创建DataFrame
            df = pd.DataFrame(export_data)
            
            # 根据格式类型导出文件
            if format_type == 'csv':
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="materials.csv"'
                df.to_csv(response, index=False, encoding='utf-8-sig')
            else:  # excel
                response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                response['Content-Disposition'] = 'attachment; filename="materials.xlsx"'
                with pd.ExcelWriter(response, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Materials')
            
            return response
            
        except Exception as e:
            logger.error(f"导出材料数据失败: {str(e)}")
            return Response({'error': f'导出失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ProcessViewSet(viewsets.ModelViewSet):
    """工艺视图集"""
    queryset = Process.objects.all().order_by('-entry_time')
    serializer_class = ProcessSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['fabrication']
    search_fields = ['fabrication', 'process_id']  # 添加 process_id 到搜索字段
    ordering_fields = ['entry_time', 'modify_time']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """重写get_queryset方法以支持更灵活的查询"""
        queryset = super().get_queryset()
        
        # 获取搜索参数
        search_query = self.request.query_params.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(fabrication__icontains=search_query) |
                Q(process_id__icontains=search_query)
            )
        
        return queryset

    def list(self, request, *args, **kwargs):
        """重写list方法以支持搜索"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """创建工艺"""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            process = serializer.save()
            return Response({
                'message': '创建成功',
                'data': self.get_serializer(process).data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"创建工艺失败: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """更新工艺"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            process = serializer.save()
            return Response({
                'message': '更新成功',
                'data': self.get_serializer(process).data
            })
        except Exception as e:
            logger.error(f"更新工艺失败: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def import_data(self, request):
        """导入工艺数据"""
        try:
            file = request.FILES.get('file')
            if not file:
                return Response({'error': '请选择要导入的文件'}, status=status.HTTP_400_BAD_REQUEST)

            # 验证文件类型
            if not file.name.endswith(('.xlsx', '.xls')):
                return Response({'error': '只支持Excel文件格式'}, status=status.HTTP_400_BAD_REQUEST)

            # 读取Excel文件
            df = pd.read_excel(file)
            
            success_count = 0
            error_messages = []
            
            with transaction.atomic():
                for index, row in df.iterrows():
                    try:
                        process_data = {
                            'fabrication': str(row.get('fabrication', '')).strip(),
                            'homogenization': bool(row.get('homogenization', 0)),
                            'homogenize_temp': float(row.get('homogenize_temp', 0)) if pd.notna(row.get('homogenize_temp')) else None,
                            'homogenize_time': float(row.get('homogenize_time', 0)) if pd.notna(row.get('homogenize_time')) else None,
                            'normalization': bool(row.get('normalization', 0)),
                            'normalize_temp': float(row.get('normalize_temp', 0)) if pd.notna(row.get('normalize_temp')) else None,
                            'normalize_time': float(row.get('normalize_time', 0)) if pd.notna(row.get('normalize_time')) else None,
                            'annealing': bool(row.get('annealing', 0)),
                            'annealing_temp': float(row.get('annealing_temp', 0)) if pd.notna(row.get('annealing_temp')) else None,
                            'annealing_time': float(row.get('annealing_time', 0)) if pd.notna(row.get('annealing_time')) else None,
                            'tempering': bool(row.get('tempering', 0)),
                            'tempering_temp': float(row.get('tempering_temp', 0)) if pd.notna(row.get('tempering_temp')) else None,
                            'tempering_time': float(row.get('tempering_time', 0)) if pd.notna(row.get('tempering_time')) else None,
                            'quenching': bool(row.get('quenching', 0)),
                            'quenching_type': str(row.get('quenching_type', '')).strip() if pd.notna(row.get('quenching_type')) else None,
                            'quenching_temp': float(row.get('quenching_temp', 0)) if pd.notna(row.get('quenching_temp')) else None,
                            'rolling': bool(row.get('rolling', 0)),
                            'rolling_temp': float(row.get('rolling_temp', 0)) if pd.notna(row.get('rolling_temp')) else None,
                            'reduction': float(row.get('reduction', 0)) if pd.notna(row.get('reduction')) else None,
                        }

                        # 验证必填字段
                        if not process_data['fabrication']:
                            error_messages.append(f"第{index + 2}行: 制备工艺不能为空")
                            continue

                        # 创建工艺记录
                        serializer = self.get_serializer(data=process_data)
                        if serializer.is_valid():
                            serializer.save()
                            success_count += 1
                        else:
                            error_messages.append(f"第{index + 2}行数据验证失败: {serializer.errors}")
                    except Exception as e:
                        error_messages.append(f"第{index + 2}行数据处理失败: {str(e)}")

            response_data = {
                'message': f'成功导入{success_count}条数据',
                'success': True,
                'total': len(df),
                'success_count': success_count
            }
            if error_messages:
                response_data['errors'] = error_messages

            if success_count > 0:
                return Response(response_data, status=status.HTTP_201_CREATED)
            else:
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"导入工艺数据失败: {str(e)}")
            return Response({'error': f'导入失败: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def export_data(self, request):
        """导出工艺数据"""
        try:
            format_type = request.data.get('format', 'excel')
            process_ids = request.data.get('process_ids', [])
            
            # 获取要导出的工艺数据
            queryset = Process.objects.all().order_by('-entry_time')
            if process_ids:
                queryset = queryset.filter(id__in=process_ids)
            
            # 准备导出数据
            export_data = []
            for process in queryset:
                # 转换时间为本地时区
                entry_time = timezone.localtime(process.entry_time) if process.entry_time.tzinfo else timezone.localtime(timezone.make_aware(process.entry_time))
                modify_time = timezone.localtime(process.modify_time) if process.modify_time.tzinfo else timezone.localtime(timezone.make_aware(process.modify_time))
                
                process_data = {
                    'process_id': process.process_id,
                    'fabrication': process.fabrication,
                    'homogenization': process.homogenization,
                    'homogenize_temp': process.homogenize_temp,
                    'homogenize_time': process.homogenize_time,
                    'normalization': process.normalization,
                    'normalize_temp': process.normalize_temp,
                    'normalize_time': process.normalize_time,
                    'annealing': process.annealing,
                    'annealing_temp': process.annealing_temp,
                    'annealing_time': process.annealing_time,
                    'tempering': process.tempering,
                    'tempering_temp': process.tempering_temp,
                    'tempering_time': process.tempering_time,
                    'quenching': process.quenching,
                    'quenching_type': process.quenching_type,
                    'quenching_temp': process.quenching_temp,
                    'rolling': process.rolling,
                    'rolling_temp': process.rolling_temp,
                    'reduction': process.reduction,
                    'entry_time': entry_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'modify_time': modify_time.strftime('%Y-%m-%d %H:%M:%S')
                }
                export_data.append(process_data)
            
            # 创建DataFrame
            df = pd.DataFrame(export_data)
            
            # 根据格式类型导出文件
            if format_type == 'csv':
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="processes.csv"'
                df.to_csv(response, index=False, encoding='utf-8-sig')
            else:  # excel
                response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                response['Content-Disposition'] = 'attachment; filename="processes.xlsx"'
                with pd.ExcelWriter(response, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Processes')
            
            return response
            
        except Exception as e:
            logger.error(f"导出工艺数据失败: {str(e)}")
            return Response({'error': f'导出失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RoomTempPropertyViewSet(viewsets.ModelViewSet):
    """室温结构性能视图集"""
    queryset = RoomTempProperty.objects.all().order_by('-entry_time')
    serializer_class = RoomTempPropertySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['material__material_id', 'process__process_id']
    search_fields = ['phase_structure']
    ordering_fields = ['entry_time', 'modify_time']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """重写get_queryset方法以支持更灵活的查询"""
        queryset = super().get_queryset()
        
        # 获取查询参数
        material_id = self.request.query_params.get('material_id')
        process_id = self.request.query_params.get('process_id')
        phase_structure = self.request.query_params.get('phase_structure')
        
        # 获取范围查询参数
        hardness_min = self.request.query_params.get('hardness_min')
        hardness_max = self.request.query_params.get('hardness_max')
        yield_strength_c_min = self.request.query_params.get('yield_strength_c_min')
        yield_strength_c_max = self.request.query_params.get('yield_strength_c_max')
        yield_strength_t_min = self.request.query_params.get('yield_strength_t_min')
        yield_strength_t_max = self.request.query_params.get('yield_strength_t_max')
        ultimate_strength_c_min = self.request.query_params.get('ultimate_strength_c_min')
        ultimate_strength_c_max = self.request.query_params.get('ultimate_strength_c_max')
        ultimate_strength_t_min = self.request.query_params.get('ultimate_strength_t_min')
        ultimate_strength_t_max = self.request.query_params.get('ultimate_strength_t_max')
        fracture_strain_c_min = self.request.query_params.get('fracture_strain_c_min')
        fracture_strain_c_max = self.request.query_params.get('fracture_strain_c_max')
        fracture_strain_t_min = self.request.query_params.get('fracture_strain_t_min')
        fracture_strain_t_max = self.request.query_params.get('fracture_strain_t_max')
        
        # 应用基本过滤条件
        if material_id:
            queryset = queryset.filter(material__material_id=material_id)
        if process_id:
            queryset = queryset.filter(process__process_id=process_id)
        if phase_structure:
            queryset = queryset.filter(phase_structure__icontains=phase_structure)
            
        # 应用范围查询条件
        if hardness_min is not None:
            queryset = queryset.filter(hardness_value__gte=float(hardness_min))
        if hardness_max is not None:
            queryset = queryset.filter(hardness_value__lte=float(hardness_max))
            
        if yield_strength_c_min is not None:
            queryset = queryset.filter(yield_strength_c__gte=float(yield_strength_c_min))
        if yield_strength_c_max is not None:
            queryset = queryset.filter(yield_strength_c__lte=float(yield_strength_c_max))
            
        if yield_strength_t_min is not None:
            queryset = queryset.filter(yield_strength_t__gte=float(yield_strength_t_min))
        if yield_strength_t_max is not None:
            queryset = queryset.filter(yield_strength_t__lte=float(yield_strength_t_max))
            
        if ultimate_strength_c_min is not None:
            queryset = queryset.filter(ultimate_strength_c__gte=float(ultimate_strength_c_min))
        if ultimate_strength_c_max is not None:
            queryset = queryset.filter(ultimate_strength_c__lte=float(ultimate_strength_c_max))
            
        if ultimate_strength_t_min is not None:
            queryset = queryset.filter(ultimate_strength_t__gte=float(ultimate_strength_t_min))
        if ultimate_strength_t_max is not None:
            queryset = queryset.filter(ultimate_strength_t__lte=float(ultimate_strength_t_max))
            
        if fracture_strain_c_min is not None:
            queryset = queryset.filter(fracture_strain_c__gte=float(fracture_strain_c_min))
        if fracture_strain_c_max is not None:
            queryset = queryset.filter(fracture_strain_c__lte=float(fracture_strain_c_max))
            
        if fracture_strain_t_min is not None:
            queryset = queryset.filter(fracture_strain_t__gte=float(fracture_strain_t_min))
        if fracture_strain_t_max is not None:
            queryset = queryset.filter(fracture_strain_t__lte=float(fracture_strain_t_max))
        
        return queryset

    def list(self, request, *args, **kwargs):
        """获取室温结构性能列表"""
        try:
            logger.debug(f"List request params: {request.query_params}")
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                response_data = self.get_paginated_response(serializer.data)
                logger.debug(f"Paginated response data count: {len(serializer.data)}")
                return response_data
            
            serializer = self.get_serializer(queryset, many=True)
            response_data = {
                'results': serializer.data,
                'count': queryset.count()
            }
            logger.debug(f"Non-paginated response data count: {len(serializer.data)}")
            return Response(response_data)
        except Exception as e:
            logger.error(f"获取室温结构性能列表失败: {str(e)}")
            return Response({'error': f'获取数据失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        """创建室温结构性能记录"""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except serializers.ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"创建室温结构性能记录失败: {str(e)}")
            return Response({'error': f'创建失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        """更新室温结构性能记录"""
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        except serializers.ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"更新室温结构性能记录失败: {str(e)}")
            return Response({'error': f'更新失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        """删除室温结构性能记录"""
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error(f"删除室温结构性能记录失败: {str(e)}")
            return Response({'error': f'删除失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['POST'])
    def import_data(self, request):
        try:
            if 'file' not in request.FILES:
                return Response({'error': '请选择要导入的文件'}, status=400)

            file = request.FILES['file']
            if not file.name.endswith(('.xls', '.xlsx')):
                return Response({'error': '只支持Excel文件格式'}, status=400)

            # 读取Excel文件
            try:
                df = pd.read_excel(file)
            except Exception as e:
                logger.error(f"Excel读取错误: {str(e)}")
                return Response({'error': f'Excel文件读取失败: {str(e)}'}, status=400)

            # 验证必需列
            required_columns = ['material_id', 'process_id', 'phase_structure']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                return Response({
                    'error': f'Excel文件缺少必需列: {", ".join(missing_columns)}'
                }, status=400)
            
            success_count = 0
            errors = []
            
            # 开启事务
            with transaction.atomic():
                for index, row in df.iterrows():
                    try:
                        # 数据验证和类型转换（兼容 Excel 整数列被读成 7043.0）
                        material_id = self._safe_int_id(row.get('material_id'))
                        process_id = self._safe_int_id(row.get('process_id'))
                        if material_id is None:
                            errors.append(f"第{index + 2}行: material_id 格式不正确（应为整数）")
                            continue
                        if process_id is None:
                            errors.append(f"第{index + 2}行: process_id 格式不正确（应为整数）")
                            continue
                        
                        # 验证material和process是否存在
                        try:
                            material = Material.objects.get(material_id=material_id)
                        except Material.DoesNotExist:
                            errors.append(f"第{index + 2}行: 材料ID {material_id} 不存在")
                            continue
                            
                        try:
                            process = Process.objects.get(process_id=process_id)
                        except Process.DoesNotExist:
                            errors.append(f"第{index + 2}行: 工艺ID {process_id} 不存在")
                            continue

                        # 准备数据
                        property_data = {
                            'material': material,
                            'process': process,
                            'phase_structure': str(row.get('phase_structure', '')).strip(),
                            'hardness_value': self._safe_float(row.get('hardness_value')),
                            'yield_strength_c': self._safe_float(row.get('yield_strength_c')),
                            'yield_strength_t': self._safe_float(row.get('yield_strength_t')),
                            'ultimate_strength_c': self._safe_float(row.get('ultimate_strength_c')),
                            'ultimate_strength_t': self._safe_float(row.get('ultimate_strength_t')),
                            'fracture_strain_c': self._safe_float(row.get('fracture_strain_c')),
                            'fracture_strain_t': self._safe_float(row.get('fracture_strain_t'))
                        }

                        # 创建或更新记录
                        obj, created = RoomTempProperty.objects.update_or_create(
                            material=material,
                            process=process,
                            defaults=property_data
                        )
                        success_count += 1

                    except Exception as e:
                        logger.error(f"导入第{index + 2}行数据时出错: {str(e)}")
                        errors.append(f"第{index + 2}行: {str(e)}")

            # 返回导入结果
            response_data = {
                'success': len(errors) == 0,
                'message': f'成功导入 {success_count} 条记录' + (f', 失败 {len(errors)} 条' if errors else ''),
                'success_count': success_count,
                'error_count': len(errors),
                'errors': errors[:10] if errors else []  # 只返回前10个错误
            }
            
            return Response(response_data)

        except Exception as e:
            logger.error(f"导入数据时发生错误: {str(e)}")
            return Response({
                'error': f'导入失败: {str(e)}',
                'success': False
            }, status=500)

    def _safe_float(self, value):
        """安全转换数值类型"""
        if pd.isna(value) or value == '':
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    def _safe_int_id(self, value):
        """安全转换整型ID，兼容 Excel 导入的 7043.0 形式。"""
        if pd.isna(value):
            return None
        s = str(value).strip()
        if s == '':
            return None
        try:
            # 先按浮点解析，确保 "7043.0" 可转
            f = float(s)
        except (ValueError, TypeError):
            return None
        if not f.is_integer():
            return None
        return int(f)

    @action(detail=False, methods=['post'])
    def export_data(self, request):
        """导出室温结构性能数据"""
        try:
            format_type = request.data.get('format', 'excel')
            property_ids = request.data.get('property_ids', [])
            
            # 获取要导出的数据
            queryset = self.get_queryset()
            if property_ids:
                queryset = queryset.filter(rtproperty_id__in=property_ids)
            
            # 准备导出数据
            export_data = []
            for property in queryset:
                # 转换时间为本地时区
                entry_time = timezone.localtime(property.entry_time) if property.entry_time.tzinfo else timezone.localtime(timezone.make_aware(property.entry_time))
                modify_time = timezone.localtime(property.modify_time) if property.modify_time.tzinfo else timezone.localtime(timezone.make_aware(property.modify_time))
                
                property_data = {
                    'rtproperty_id': property.rtproperty_id,
                    'material_id': property.material.material_id,
                    'process_id': property.process.process_id,
                    'phase_structure': property.phase_structure,
                    'hardness_value': property.hardness_value,
                    'yield_strength_c': property.yield_strength_c,
                    'yield_strength_t': property.yield_strength_t,
                    'ultimate_strength_c': property.ultimate_strength_c,
                    'ultimate_strength_t': property.ultimate_strength_t,
                    'fracture_strain_c': property.fracture_strain_c,
                    'fracture_strain_t': property.fracture_strain_t,
                    'entry_time': entry_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'modify_time': modify_time.strftime('%Y-%m-%d %H:%M:%S')
                }
                export_data.append(property_data)
            
            # 创建DataFrame
            df = pd.DataFrame(export_data)
            
            # 根据格式类型导出文件
            if format_type == 'csv':
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="room_temp_properties.csv"'
                df.to_csv(response, index=False, encoding='utf-8-sig')
            else:  # excel
                response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                response['Content-Disposition'] = 'attachment; filename="room_temp_properties.xlsx"'
                with pd.ExcelWriter(response, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='RoomTempProperties')
            
            return response
            
        except Exception as e:
            logger.error(f"导出室温结构性能数据失败: {str(e)}")
            return Response({'error': f'导出失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 

class HTPropertyViewSet(viewsets.ModelViewSet):
    """高温力学性能视图集"""
    queryset = HTProperty.objects.all().order_by('-entry_time')
    serializer_class = HTPropertySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['material__material_id', 'process__process_id', 'test_type']
    search_fields = ['test_type']
    ordering_fields = ['entry_time', 'modify_time', 'htproperty_temp']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """重写get_queryset方法以支持更灵活的查询"""
        queryset = super().get_queryset()
        
        # 获取查询参数
        material_id = self.request.query_params.get('material_id')
        process_id = self.request.query_params.get('process_id')
        test_type = self.request.query_params.get('test_type')
        
        # 获取范围查询参数
        temp_min = self.request.query_params.get('htproperty_temp_min')
        temp_max = self.request.query_params.get('htproperty_temp_max')
        yield_strength_min = self.request.query_params.get('yield_strength_min')
        yield_strength_max = self.request.query_params.get('yield_strength_max')
        ultimate_strength_min = self.request.query_params.get('ultimate_strength_min')
        ultimate_strength_max = self.request.query_params.get('ultimate_strength_max')
        fracture_strain_min = self.request.query_params.get('fracture_strain_min')
        fracture_strain_max = self.request.query_params.get('fracture_strain_max')
        
        # 应用基本过滤条件
        if material_id:
            queryset = queryset.filter(material__material_id=material_id)
        if process_id:
            queryset = queryset.filter(process__process_id=process_id)
        if test_type:
            queryset = queryset.filter(test_type__icontains=test_type)
            
        # 应用范围查询条件
        if temp_min is not None:
            queryset = queryset.filter(htproperty_temp__gte=float(temp_min))
        if temp_max is not None:
            queryset = queryset.filter(htproperty_temp__lte=float(temp_max))
            
        if yield_strength_min is not None:
            queryset = queryset.filter(yield_strength__gte=float(yield_strength_min))
        if yield_strength_max is not None:
            queryset = queryset.filter(yield_strength__lte=float(yield_strength_max))
            
        if ultimate_strength_min is not None:
            queryset = queryset.filter(ultimate_strength__gte=float(ultimate_strength_min))
        if ultimate_strength_max is not None:
            queryset = queryset.filter(ultimate_strength__lte=float(ultimate_strength_max))
            
        if fracture_strain_min is not None:
            queryset = queryset.filter(fracture_strain__gte=float(fracture_strain_min))
        if fracture_strain_max is not None:
            queryset = queryset.filter(fracture_strain__lte=float(fracture_strain_max))
        
        return queryset

    def list(self, request, *args, **kwargs):
        """获取高温力学性能列表"""
        try:
            logger.debug(f"List request params: {request.query_params}")
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                response_data = self.get_paginated_response(serializer.data)
                logger.debug(f"Paginated response data count: {len(serializer.data)}")
                return response_data
            
            serializer = self.get_serializer(queryset, many=True)
            response_data = {
                'results': serializer.data,
                'count': queryset.count()
            }
            logger.debug(f"Non-paginated response data count: {len(serializer.data)}")
            return Response(response_data)
        except Exception as e:
            logger.error(f"获取高温力学性能列表失败: {str(e)}")
            return Response({'error': f'获取数据失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        """创建高温力学性能记录"""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except serializers.ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"创建高温力学性能记录失败: {str(e)}")
            return Response({'error': f'创建失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        """更新高温力学性能记录"""
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        except serializers.ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"更新高温力学性能记录失败: {str(e)}")
            return Response({'error': f'更新失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        """删除高温力学性能记录"""
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error(f"删除高温力学性能记录失败: {str(e)}")
            return Response({'error': f'删除失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['POST'])
    def import_data(self, request):
        """导入高温力学性能数据"""
        try:
            if 'file' not in request.FILES:
                return Response({'error': '请选择要导入的文件'}, status=400)

            file = request.FILES['file']
            if not file.name.endswith(('.xls', '.xlsx')):
                return Response({'error': '只支持Excel文件格式'}, status=400)

            # 读取Excel文件
            try:
                df = pd.read_excel(file)
            except Exception as e:
                logger.error(f"Excel读取错误: {str(e)}")
                return Response({'error': f'Excel文件读取失败: {str(e)}'}, status=400)

            # 验证必需列
            required_columns = ['material_id', 'process_id', 'test_type', 'htproperty_temp']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                return Response({
                    'error': f'Excel文件缺少必需列: {", ".join(missing_columns)}'
                }, status=400)
            
            success_count = 0
            errors = []
            
            # 开启事务
            with transaction.atomic():
                for index, row in df.iterrows():
                    try:
                        # 数据验证和类型转换
                        material_id = str(row['material_id']).strip()
                        process_id = str(row['process_id']).strip()
                        
                        # 验证material和process是否存在
                        try:
                            material = Material.objects.get(material_id=material_id)
                        except Material.DoesNotExist:
                            errors.append(f"第{index + 2}行: 材料ID {material_id} 不存在")
                            continue
                            
                        try:
                            process = Process.objects.get(process_id=process_id)
                        except Process.DoesNotExist:
                            errors.append(f"第{index + 2}行: 工艺ID {process_id} 不存在")
                            continue

                        # 准备数据
                        property_data = {
                            'material': material,
                            'process': process,
                            'test_type': str(row.get('test_type', '')).strip(),
                            'htproperty_temp': self._safe_float(row.get('htproperty_temp')),
                            'yield_strength': self._safe_float(row.get('yield_strength')),
                            'ultimate_strength': self._safe_float(row.get('ultimate_strength')),
                            'fracture_strain': self._safe_float(row.get('fracture_strain'))
                        }

                        # 验证必填字段
                        if not property_data['test_type']:
                            errors.append(f"第{index + 2}行: 测试类型不能为空")
                            continue
                            
                        if property_data['htproperty_temp'] is None:
                            errors.append(f"第{index + 2}行: 测试温度不能为空")
                            continue

                        # 创建或更新记录
                        obj, created = HTProperty.objects.update_or_create(
                            material=material,
                            process=process,
                            test_type=property_data['test_type'],
                            htproperty_temp=property_data['htproperty_temp'],
                            defaults={
                                'yield_strength': property_data['yield_strength'],
                                'ultimate_strength': property_data['ultimate_strength'],
                                'fracture_strain': property_data['fracture_strain']
                            }
                        )
                        success_count += 1

                    except Exception as e:
                        logger.error(f"导入第{index + 2}行数据时出错: {str(e)}")
                        errors.append(f"第{index + 2}行: {str(e)}")

            # 返回导入结果
            response_data = {
                'success': len(errors) == 0,
                'message': f'成功导入 {success_count} 条记录' + (f', 失败 {len(errors)} 条' if errors else ''),
                'success_count': success_count,
                'error_count': len(errors),
                'errors': errors[:10] if errors else []  # 只返回前10个错误
            }
            
            return Response(response_data)

        except Exception as e:
            logger.error(f"导入数据时发生错误: {str(e)}")
            return Response({
                'error': f'导入失败: {str(e)}',
                'success': False
            }, status=500)

    def _safe_float(self, value):
        """安全转换数值类型"""
        if pd.isna(value) or value == '':
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    @action(detail=False, methods=['post'])
    def export_data(self, request):
        """导出高温力学性能数据"""
        try:
            format_type = request.data.get('format', 'excel')
            property_ids = request.data.get('property_ids', [])
            
            # 获取要导出的数据
            queryset = self.get_queryset()
            if property_ids:
                queryset = queryset.filter(htproperty_id__in=property_ids)
            
            # 准备导出数据
            export_data = []
            for property in queryset:
                # 转换时间为本地时区
                entry_time = timezone.localtime(property.entry_time) if property.entry_time.tzinfo else timezone.localtime(timezone.make_aware(property.entry_time))
                modify_time = timezone.localtime(property.modify_time) if property.modify_time.tzinfo else timezone.localtime(timezone.make_aware(property.modify_time))
                
                property_data = {
                    'htproperty_id': property.htproperty_id,
                    'material_id': property.material.material_id,
                    'process_id': property.process.process_id,
                    'test_type': property.test_type,
                    'htproperty_temp': property.htproperty_temp,
                    'yield_strength': property.yield_strength,
                    'ultimate_strength': property.ultimate_strength,
                    'fracture_strain': property.fracture_strain,
                    'entry_time': entry_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'modify_time': modify_time.strftime('%Y-%m-%d %H:%M:%S')
                }
                export_data.append(property_data)
            
            # 创建DataFrame
            df = pd.DataFrame(export_data)
            
            # 根据格式类型导出文件
            if format_type == 'csv':
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="ht_properties.csv"'
                df.to_csv(response, index=False, encoding='utf-8-sig')
            else:  # excel
                response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                response['Content-Disposition'] = 'attachment; filename="ht_properties.xlsx"'
                with pd.ExcelWriter(response, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='HTProperties')
            
            return response
            
        except Exception as e:
            logger.error(f"导出高温力学性能数据失败: {str(e)}")
            return Response({'error': f'导出失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ImpTestViewSet(viewsets.ModelViewSet):
    """冲击测试表视图集"""
    queryset = ImpTest.objects.all()
    serializer_class = ImpTestSerializer

    def get_queryset(self):
        queryset = ImpTest.objects.all()
        material_id = self.request.query_params.get('material_id')
        process_id = self.request.query_params.get('process_id')
        impact_type = self.request.query_params.get('impact_type')
        fracture_type = self.request.query_params.get('fracture_type')
        
        # 获取范围查询参数
        impact_energy_min = self.request.query_params.get('impact_energy_min')
        impact_energy_max = self.request.query_params.get('impact_energy_max')
        absorbed_energy_min = self.request.query_params.get('absorbed_energy_min')
        absorbed_energy_max = self.request.query_params.get('absorbed_energy_max')
        impact_tough_value_min = self.request.query_params.get('impact_tough_value_min')
        impact_tough_value_max = self.request.query_params.get('impact_tough_value_max')
        
        # 构建查询条件
        if material_id:
            queryset = queryset.filter(material__material_id=material_id)
        if process_id:
            queryset = queryset.filter(process__process_id=process_id)
        if impact_type:
            queryset = queryset.filter(impact_type=impact_type)
        if fracture_type:
            queryset = queryset.filter(fracture_type=fracture_type)
        
        # 应用范围查询条件
        if impact_energy_min and impact_energy_min.strip():
            queryset = queryset.filter(impact_energy__gte=float(impact_energy_min))
        if impact_energy_max and impact_energy_max.strip():
            queryset = queryset.filter(impact_energy__lte=float(impact_energy_max))
            
        if absorbed_energy_min and absorbed_energy_min.strip():
            queryset = queryset.filter(absorbed_energy__gte=float(absorbed_energy_min))
        if absorbed_energy_max and absorbed_energy_max.strip():
            queryset = queryset.filter(absorbed_energy__lte=float(absorbed_energy_max))
            
        if impact_tough_value_min and impact_tough_value_min.strip():
            queryset = queryset.filter(impact_tough_value__gte=float(impact_tough_value_min))
        if impact_tough_value_max and impact_tough_value_max.strip():
            queryset = queryset.filter(impact_tough_value__lte=float(impact_tough_value_max))
            
        return queryset

    @action(detail=False, methods=['post'])
    def import_data(self, request):
        """导入数据"""
        file = request.FILES.get('file')
        if file is None:
            return Response({"detail": "未提供文件"}, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查文件类型
        if not (file.name.endswith('.xlsx') or file.name.endswith('.csv')):
            return Response({"detail": "仅支持 .xlsx 或 .csv 文件"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            if file.name.endswith('.xlsx'):
                data = pd.read_excel(file)
            else:
                data = pd.read_csv(file)
            
            # 验证数据结构
            required_columns = ['material_id', 'process_id']
            missing_columns = [col for col in required_columns if col not in data.columns]
            if missing_columns:
                return Response(
                    {"detail": f"缺少必要的列: {', '.join(missing_columns)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            results = {
                'success': 0,
                'failure': 0,
                'errors': []
            }
            
            # 处理每一行数据
            for index, row in data.iterrows():
                try:
                    row_dict = row.to_dict()
                    # 清除NaN值
                    row_dict = {k: v for k, v in row_dict.items() if pd.notna(v)}
                    
                    serializer = self.get_serializer(data=row_dict)
                    if serializer.is_valid():
                        serializer.save()
                        results['success'] += 1
                    else:
                        error_detail = {
                            'row': index + 2,  # 考虑到表头和从0开始的索引
                            'errors': serializer.errors
                        }
                        results['errors'].append(error_detail)
                        results['failure'] += 1
                except Exception as e:
                    error_detail = {
                        'row': index + 2,
                        'errors': str(e)
                    }
                    results['errors'].append(error_detail)
                    results['failure'] += 1
            
            return Response(results, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def export_data(self, request):
        """导出数据"""
        # 获取要导出的ID列表
        property_ids = request.data.get('property_ids', [])
        format_type = request.data.get('format', 'excel')
        
        # 根据ID过滤查询集
        if property_ids and len(property_ids) > 0:
            queryset = ImpTest.objects.filter(impact_id__in=property_ids)
        else:
            queryset = self.get_queryset()
        
        if not queryset.exists():
            return Response({"detail": "没有数据可导出"}, status=status.HTTP_404_NOT_FOUND)
        
        # 创建一个DataFrame来保存所有数据
        data = []
        for item in queryset:
            # 确保时间格式一致，通过转换为本地时区
            entry_time = timezone.localtime(item.entry_time) if item.entry_time.tzinfo else timezone.localtime(timezone.make_aware(item.entry_time))
            modify_time = timezone.localtime(item.modify_time) if item.modify_time.tzinfo else timezone.localtime(timezone.make_aware(item.modify_time))
            
            entry_time_str = entry_time.strftime('%Y-%m-%d %H:%M:%S')
            modify_time_str = modify_time.strftime('%Y-%m-%d %H:%M:%S')
            
            data.append({
                'impact_id': item.impact_id,
                'material_id': item.material.material_id,
                'material_name': item.material.material_name if hasattr(item.material, 'material_name') else None,
                'process_id': item.process.process_id,
                'fabrication': item.process.fabrication if hasattr(item.process, 'fabrication') else None,
                'impact_temp': item.impact_temp,
                'impact_type': item.impact_type,
                'impact_energy': item.impact_energy,
                'absorbed_energy': item.absorbed_energy,
                'impact_tough_value': item.impact_tough_value,
                'fracture_type': item.fracture_type,
                'entry_time': entry_time_str,
                'modify_time': modify_time_str
            })
        
        df = pd.DataFrame(data)
        
        # 根据格式类型导出
        if format_type == 'excel':
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            
            output.seek(0)
            response = HttpResponse(
                output.read(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename="imp_test_data.xlsx"'
            return response
        
        elif format_type == 'csv':
            output = io.StringIO()
            df.to_csv(output, index=False)
            
            response = HttpResponse(output.getvalue(), content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="imp_test_data.csv"'
            return response
        
        else:
            return Response({"detail": "不支持的导出格式"}, status=status.HTTP_400_BAD_REQUEST)

class CreTestViewSet(viewsets.ModelViewSet):
    """蠕变测试表视图集"""
    queryset = CreTest.objects.all().order_by('-entry_time')
    serializer_class = CreTestSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['material__material_id', 'process__process_id']
    search_fields = ['creep_id']
    ordering_fields = ['entry_time', 'modify_time', 'creep_temp', 'creep_time', 'rupture_time']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """重写get_queryset方法以支持更灵活的查询"""
        queryset = super().get_queryset()
        
        # 获取查询参数
        material_id = self.request.query_params.get('material_id')
        process_id = self.request.query_params.get('process_id')
        
        # 获取范围查询参数
        creep_temp_min = self.request.query_params.get('creep_temp_min')
        creep_temp_max = self.request.query_params.get('creep_temp_max')
        creep_time_min = self.request.query_params.get('creep_time_min')
        creep_time_max = self.request.query_params.get('creep_time_max')
        initial_stress_min = self.request.query_params.get('initial_stress_min')
        initial_stress_max = self.request.query_params.get('initial_stress_max')
        creep_rate_min = self.request.query_params.get('creep_rate_min')
        creep_rate_max = self.request.query_params.get('creep_rate_max')
        creep_limit_min = self.request.query_params.get('creep_limit_min')
        creep_limit_max = self.request.query_params.get('creep_limit_max')
        creep_rupture_strength_min = self.request.query_params.get('creep_rupture_strength_min')
        creep_rupture_strength_max = self.request.query_params.get('creep_rupture_strength_max')
        rupture_time_min = self.request.query_params.get('rupture_time_min')
        rupture_time_max = self.request.query_params.get('rupture_time_max')
        rupture_strength_limit_min = self.request.query_params.get('rupture_strength_limit_min')
        rupture_strength_limit_max = self.request.query_params.get('rupture_strength_limit_max')
        percentage_elongation_min = self.request.query_params.get('percentage_elongation_min')
        percentage_elongation_max = self.request.query_params.get('percentage_elongation_max')
        
        # 定义一个安全过滤函数
        def safe_filter(queryset, field_name, op, value):
            """安全的过滤函数，避免非法输入"""
            try:
                if value is not None and value != '':
                    value = float(value)
                    filter_kwargs = {f'{field_name}__{op}': value}
                    queryset = queryset.filter(**filter_kwargs)
            except (ValueError, TypeError) as e:
                logger.warning(f"过滤字段 {field_name} 的值 {value} 无效: {str(e)}")
            return queryset
            
        # 基于材料ID和工艺ID过滤
        if material_id:
            queryset = queryset.filter(material__material_id=material_id)
        if process_id:
            queryset = queryset.filter(process__process_id=process_id)
            
        # 范围过滤
        queryset = safe_filter(queryset, 'creep_temp', 'gte', creep_temp_min)
        queryset = safe_filter(queryset, 'creep_temp', 'lte', creep_temp_max)
        queryset = safe_filter(queryset, 'creep_time', 'gte', creep_time_min)
        queryset = safe_filter(queryset, 'creep_time', 'lte', creep_time_max)
        queryset = safe_filter(queryset, 'initial_stress', 'gte', initial_stress_min)
        queryset = safe_filter(queryset, 'initial_stress', 'lte', initial_stress_max)
        queryset = safe_filter(queryset, 'creep_rate', 'gte', creep_rate_min)
        queryset = safe_filter(queryset, 'creep_rate', 'lte', creep_rate_max)
        queryset = safe_filter(queryset, 'creep_limit', 'gte', creep_limit_min)
        queryset = safe_filter(queryset, 'creep_limit', 'lte', creep_limit_max)
        queryset = safe_filter(queryset, 'creep_rupture_strength', 'gte', creep_rupture_strength_min)
        queryset = safe_filter(queryset, 'creep_rupture_strength', 'lte', creep_rupture_strength_max)
        queryset = safe_filter(queryset, 'rupture_time', 'gte', rupture_time_min)
        queryset = safe_filter(queryset, 'rupture_time', 'lte', rupture_time_max)
        queryset = safe_filter(queryset, 'rupture_strength_limit', 'gte', rupture_strength_limit_min)
        queryset = safe_filter(queryset, 'rupture_strength_limit', 'lte', rupture_strength_limit_max)
        queryset = safe_filter(queryset, 'percentage_elongation', 'gte', percentage_elongation_min)
        queryset = safe_filter(queryset, 'percentage_elongation', 'lte', percentage_elongation_max)
            
        return queryset
        
    @action(detail=False, methods=['post'])
    def export_data(self, request):
        """导出蠕变测试数据"""
        try:
            from django.utils import timezone
            
            format_type = request.data.get('format', 'excel')
            property_ids = request.data.get('property_ids', [])
            
            # 获取要导出的数据
            queryset = self.get_queryset()
            if property_ids:
                queryset = queryset.filter(creep_id__in=property_ids)
            
            # 准备导出数据
            export_data = []
            for property in queryset:
                # 转换时间为本地时区
                entry_time = timezone.localtime(property.entry_time) if property.entry_time.tzinfo else timezone.localtime(timezone.make_aware(property.entry_time))
                modify_time = timezone.localtime(property.modify_time) if property.modify_time.tzinfo else timezone.localtime(timezone.make_aware(property.modify_time))
                
                export_data.append({
                    'Creep Test ID': property.creep_id,
                    'Material ID': property.material.material_id,
                    'Process ID': property.process.process_id,
                    'Test Temperature': property.creep_temp,
                    'Test Time': property.creep_time,
                    'Initial Stress': property.initial_stress,
                    'Steady-State Creep Rate': property.creep_rate,
                    'Creep Limit': property.creep_limit,
                    'Creep Rupture Strength': property.creep_rupture_strength,
                    'Rupture Time': property.rupture_time,
                    'Rupture Strength Limit': property.rupture_strength_limit,
                    'Elongation After Fracture': property.percentage_elongation,
                    'Entry Time': entry_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'Updated At': modify_time.strftime('%Y-%m-%d %H:%M:%S'),
                })
            
            if not export_data:
                return Response({"detail": "没有数据可导出"}, status=status.HTTP_404_NOT_FOUND)
            
            # 将数据转换为DataFrame
            df = pd.DataFrame(export_data)
            
            # 根据format_type返回不同格式的数据
            if format_type == 'excel':
                # 创建一个excel writer
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, sheet_name='Creep Tests', index=False)
                
                # 设置response的headers和content_type
                output.seek(0)
                filename = f"creep_test_data_{timezone.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                response = Response(output.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                return response
            elif format_type == 'csv':
                # 创建一个CSV
                output = io.StringIO()
                df.to_csv(output, index=False)
                
                # 设置response的headers和content_type
                output.seek(0)
                filename = f"creep_test_data_{timezone.now().strftime('%Y%m%d_%H%M%S')}.csv"
                response = Response(output.getvalue(), content_type='text/csv')
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                return response
            else:
                return Response({"detail": "不支持的导出格式"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"导出蠕变测试数据时发生错误: {str(e)}")
            return Response({"detail": f"导出失败: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def import_data(self, request):
        """导入蠕变测试数据"""
        try:
            file = request.FILES.get('file')
            if not file:
                return Response({"detail": "请选择一个文件"}, status=status.HTTP_400_BAD_REQUEST)
            
            # 根据文件扩展名确定读取方法
            file_name = file.name.lower()
            if file_name.endswith('.xlsx') or file_name.endswith('.xls'):
                df = pd.read_excel(file)
            elif file_name.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                return Response({"detail": "不支持的文件格式，请使用Excel或CSV文件"}, status=status.HTTP_400_BAD_REQUEST)

            # Keep legacy Chinese templates compatible while accepting current English exports.
            english_aliases = {
                'Creep Test ID': '蠕变测试ID',
                'Material ID': '材料ID',
                'Process ID': '工艺ID',
                'Test Temperature': '测试温度',
                'Test Time': '测试时间',
                'Initial Stress': '初始应力',
                'Steady-State Creep Rate': '稳态蠕变速率',
                'Creep Limit': '蠕变极限',
                'Creep Rupture Strength': '蠕变持久强度',
                'Rupture Time': '断裂时间',
                'Rupture Strength Limit': '持久强度极限',
                'Elongation After Fracture': '断后伸长率',
            }
            df.rename(
                columns={
                    english: legacy
                    for english, legacy in english_aliases.items()
                    if english in df.columns and legacy not in df.columns
                },
                inplace=True,
            )
            
            # 验证文件结构
            required_columns = ['材料ID', '工艺ID', '测试温度']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                return Response({"detail": f"文件缺少必要的列：{', '.join(missing_columns)}"}, status=status.HTTP_400_BAD_REQUEST)
            
            # 处理导入数据
            success_count = 0
            error_records = []
            
            for _, row in df.iterrows():
                try:
                    material_id = row['材料ID']
                    process_id = row['工艺ID']
                    
                    # 验证材料和工艺是否存在
                    try:
                        material = Material.objects.get(material_id=material_id)
                        process = Process.objects.get(process_id=process_id)
                    except Material.DoesNotExist:
                        error_records.append({
                            "row": _+2,  # Excel行号从1开始，并且有标题行
                            "error": f"材料ID {material_id} 不存在"
                        })
                        continue
                    except Process.DoesNotExist:
                        error_records.append({
                            "row": _+2,
                            "error": f"工艺ID {process_id} 不存在"
                        })
                        continue
                    
                    # 准备创建或更新的数据
                    data = {
                        'material': material,
                        'process': process,
                        'creep_temp': row.get('测试温度'),
                        'creep_time': row.get('测试时间'),
                        'initial_stress': row.get('初始应力'),
                        'creep_rate': row.get('稳态蠕变速率'),
                        'creep_limit': row.get('蠕变极限'),
                        'creep_rupture_strength': row.get('蠕变持久强度'),
                        'rupture_time': row.get('断裂时间'),
                        'rupture_strength_limit': row.get('持久强度极限'),
                        'percentage_elongation': row.get('断后伸长率')
                    }
                    
                    # 如果有蠕变测试ID，尝试更新，否则创建新记录
                    if '蠕变测试ID' in row and not pd.isna(row['蠕变测试ID']):
                        try:
                            creep_test = CreTest.objects.get(creep_id=row['蠕变测试ID'])
                            # 更新字段
                            for key, value in data.items():
                                if value is not None and not pd.isna(value):
                                    setattr(creep_test, key, value)
                            creep_test.save()
                        except CreTest.DoesNotExist:
                            # 如果指定ID的记录不存在，创建新记录
                            CreTest.objects.create(**data)
                    else:
                        # 创建新记录
                        CreTest.objects.create(**data)
                    
                    success_count += 1
                except Exception as e:
                    error_records.append({
                        "row": _+2,
                        "error": str(e)
                    })
            
            # 返回导入结果
            return Response({
                "success_count": success_count,
                "error_count": len(error_records),
                "errors": error_records
            })
        except Exception as e:
            logger.error(f"导入蠕变测试数据时发生错误: {str(e)}")
            return Response({"detail": f"导入失败: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FatTestViewSet(viewsets.ModelViewSet):
    """疲劳测试表视图集"""
    queryset = FatTest.objects.all().order_by('-entry_time')
    serializer_class = FatTestSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['material__material_id', 'process__process_id']
    search_fields = ['fatigue_id']
    ordering_fields = ['entry_time', 'modify_time', 'environment_temp', 'fatigue_life', 'fatigue_limit']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """重写get_queryset方法以支持更灵活的查询"""
        queryset = super().get_queryset()
        
        # 获取查询参数
        material_id = self.request.query_params.get('material_id')
        process_id = self.request.query_params.get('process_id')
        
        # 获取范围查询参数
        stress_ratio_min = self.request.query_params.get('stress_ratio_min')
        stress_ratio_max = self.request.query_params.get('stress_ratio_max')
        stress_range_min = self.request.query_params.get('stress_range_min')
        stress_range_max = self.request.query_params.get('stress_range_max')
        mean_stress_min = self.request.query_params.get('mean_stress_min')
        mean_stress_max = self.request.query_params.get('mean_stress_max')
        loading_frequency_min = self.request.query_params.get('loading_frequency_min')
        loading_frequency_max = self.request.query_params.get('loading_frequency_max')
        environment_temp_min = self.request.query_params.get('environment_temp_min')
        environment_temp_max = self.request.query_params.get('environment_temp_max')
        fatigue_life_min = self.request.query_params.get('fatigue_life_min')
        fatigue_life_max = self.request.query_params.get('fatigue_life_max')
        fatigue_limit_min = self.request.query_params.get('fatigue_limit_min')
        fatigue_limit_max = self.request.query_params.get('fatigue_limit_max')
        
        # 定义一个安全过滤函数
        def safe_filter(queryset, field_name, op, value):
            """安全的过滤函数，避免非法输入"""
            try:
                if value is not None and value != '':
                    value = float(value)
                    filter_kwargs = {f'{field_name}__{op}': value}
                    queryset = queryset.filter(**filter_kwargs)
            except (ValueError, TypeError) as e:
                logger.warning(f"过滤字段 {field_name} 的值 {value} 无效: {str(e)}")
            return queryset
            
        # 基于材料ID和工艺ID过滤
        if material_id:
            queryset = queryset.filter(material__material_id=material_id)
        if process_id:
            queryset = queryset.filter(process__process_id=process_id)
            
        # 范围过滤
        queryset = safe_filter(queryset, 'stress_ratio', 'gte', stress_ratio_min)
        queryset = safe_filter(queryset, 'stress_ratio', 'lte', stress_ratio_max)
        queryset = safe_filter(queryset, 'stress_range', 'gte', stress_range_min)
        queryset = safe_filter(queryset, 'stress_range', 'lte', stress_range_max)
        queryset = safe_filter(queryset, 'mean_stress', 'gte', mean_stress_min)
        queryset = safe_filter(queryset, 'mean_stress', 'lte', mean_stress_max)
        queryset = safe_filter(queryset, 'loading_frequency', 'gte', loading_frequency_min)
        queryset = safe_filter(queryset, 'loading_frequency', 'lte', loading_frequency_max)
        queryset = safe_filter(queryset, 'environment_temp', 'gte', environment_temp_min)
        queryset = safe_filter(queryset, 'environment_temp', 'lte', environment_temp_max)
        queryset = safe_filter(queryset, 'fatigue_life', 'gte', fatigue_life_min)
        queryset = safe_filter(queryset, 'fatigue_life', 'lte', fatigue_life_max)
        queryset = safe_filter(queryset, 'fatigue_limit', 'gte', fatigue_limit_min)
        queryset = safe_filter(queryset, 'fatigue_limit', 'lte', fatigue_limit_max)
            
        return queryset
        
    @action(detail=False, methods=['post'])
    def export_data(self, request):
        """导出疲劳测试数据"""
        try:
            from django.utils import timezone
            from django.http import HttpResponse
            
            format_type = request.data.get('format', 'excel')
            property_ids = request.data.get('property_ids', [])
            
            # 获取要导出的数据
            queryset = self.get_queryset()
            if property_ids:
                queryset = queryset.filter(fatigue_id__in=property_ids)
            
            # 准备导出数据
            export_data = []
            for property in queryset:
                # 转换时间为本地时区
                entry_time = timezone.localtime(property.entry_time) if property.entry_time.tzinfo else timezone.localtime(timezone.make_aware(property.entry_time))
                modify_time = timezone.localtime(property.modify_time) if property.modify_time.tzinfo else timezone.localtime(timezone.make_aware(property.modify_time))
                
                export_data.append({
                    'Fatigue Test ID': property.fatigue_id,
                    'Material ID': property.material.material_id,
                    'Process ID': property.process.process_id,
                    'Test Type': property.fatigue_method,
                    'Stress Ratio': property.stress_ratio,
                    'Stress Range': property.stress_range,
                    'Mean Stress': property.mean_stress,
                    'Loading Frequency': property.loading_frequency,
                    'Environment Temperature': property.environment_temp,
                    'Fatigue Life': property.fatigue_life,
                    'Fatigue Limit': property.fatigue_limit,
                    'Entry Time': entry_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'Updated At': modify_time.strftime('%Y-%m-%d %H:%M:%S'),
                })
            
            if not export_data:
                return Response({"detail": "没有数据可导出"}, status=status.HTTP_404_NOT_FOUND)
            
            # 将数据转换为DataFrame
            df = pd.DataFrame(export_data)
            
            # 根据format_type直接返回文件响应，而非通过REST框架的Response
            if format_type == 'excel':
                # 创建一个excel文件
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, sheet_name='Fatigue Tests', index=False)
                
                # 设置response的headers和content_type
                output.seek(0)
                filename = f"fatigue_test_data_{timezone.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                response = HttpResponse(
                    output.getvalue(),
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                return response
            elif format_type == 'csv':
                # 创建一个CSV文件
                output = io.StringIO()
                df.to_csv(output, index=False)
                
                # 设置response的headers和content_type
                output.seek(0)
                filename = f"fatigue_test_data_{timezone.now().strftime('%Y%m%d_%H%M%S')}.csv"
                response = HttpResponse(
                    output.getvalue(),
                    content_type='text/csv'
                )
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                return response
            else:
                return Response({"detail": "不支持的导出格式"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"导出疲劳测试数据时发生错误: {str(e)}")
            return Response({"detail": f"导出失败: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def import_data(self, request):
        """导入疲劳测试数据"""
        try:
            file = request.FILES.get('file')
            if not file:
                return Response({"detail": "请选择一个文件"}, status=status.HTTP_400_BAD_REQUEST)
            
            # 根据文件扩展名确定读取方法
            file_name = file.name.lower()
            try:
                if file_name.endswith('.xlsx') or file_name.endswith('.xls'):
                    # 使用openpyxl引擎以支持更多Excel格式
                    df = pd.read_excel(file, engine='openpyxl')
                elif file_name.endswith('.csv'):
                    # 尝试不同编码方式读取CSV文件
                    try:
                        df = pd.read_csv(file, encoding='utf-8')
                    except UnicodeDecodeError:
                        df = pd.read_csv(file, encoding='gbk')
                else:
                    return Response({"detail": "不支持的文件格式，请使用Excel或CSV文件"}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                logger.error(f"文件读取错误: {str(e)}")
                return Response({"detail": f"文件读取错误: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
            
            # 打印出表头和前几行数据，用于调试
            logger.info(f"导入文件列名: {list(df.columns)}")
            logger.info("Fatigue import parsed: rows=%s, columns=%s", len(df), len(df.columns))
            
            # 中英文字段名映射
            field_mapping = {
                '疲劳测试ID': ['Fatigue Test ID', 'fatigue_id', 'fatigue_test_id'],
                '材料ID': ['Material ID', 'material_id'],
                '工艺ID': ['Process ID', 'process_id'],
                '测试类型': ['Test Type', 'fatigue_method', 'test_type'],
                '应力比': ['Stress Ratio', 'stress_ratio'],
                '应力幅': ['Stress Range', 'stress_range'],
                '平均应力': ['Mean Stress', 'mean_stress'],
                '加载频率': ['Loading Frequency', 'loading_frequency'],
                '环境温度': ['Environment Temperature', 'environment_temp'],
                '疲劳寿命': ['Fatigue Life', 'fatigue_life'],
                '疲劳极限': ['Fatigue Limit', 'fatigue_limit']
            }
            
            # 尝试标准化列名
            column_mapping = {}
            for zh_field, en_fields in field_mapping.items():
                # 先检查中文字段
                if zh_field in df.columns:
                    continue
                
                # 检查英文字段
                for en_field in en_fields:
                    if en_field in df.columns:
                        column_mapping[en_field] = zh_field
                        break
            
            # 如果找到了映射关系，重命名列
            if column_mapping:
                df.rename(columns=column_mapping, inplace=True)
                logger.info(f"已重命名列: {column_mapping}")
                logger.info(f"重命名后的列: {list(df.columns)}")
            
            # 验证文件结构
            required_columns = ['材料ID', '工艺ID']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                return Response({"detail": f"文件缺少必要的列：{', '.join(missing_columns)}"}, status=status.HTTP_400_BAD_REQUEST)
            
            # 处理导入数据
            success_count = 0
            auto_increment_count = 0  # 添加自增ID记录计数
            error_records = []
            
            # 使用事务确保数据一致性
            with transaction.atomic():
                for idx, row in df.iterrows():
                    try:
                        # 处理材料ID和工艺ID，确保它们是整数
                        try:
                            material_id = int(row['材料ID'])
                            process_id = int(row['工艺ID'])
                        except (ValueError, TypeError):
                            error_records.append({
                                "row": idx+2,
                                "error": f"材料ID或工艺ID必须为整数"
                            })
                            continue
                        
                        # 验证材料和工艺是否存在
                        try:
                            material = Material.objects.get(material_id=material_id)
                        except Material.DoesNotExist:
                            error_records.append({
                                "row": idx+2,
                                "error": f"材料ID {material_id} 不存在"
                            })
                            continue
                        
                        try:
                            process = Process.objects.get(process_id=process_id)
                        except Process.DoesNotExist:
                            error_records.append({
                                "row": idx+2,
                                "error": f"工艺ID {process_id} 不存在"
                            })
                            continue
                        
                        # 安全地获取数值类型的数据，确保它们都能转为浮点数
                        def safe_float(value, default=None):
                            if pd.isna(value) or value == '':
                                return default
                            try:
                                return float(value)
                            except (ValueError, TypeError):
                                return default
                        
                        # 获取字段值函数
                        def get_field_value(row, zh_field):
                            # 直接尝试获取中文字段
                            if zh_field in row:
                                return row[zh_field]
                            
                            # 如果找不到中文字段，尝试英文字段
                            for en_field in field_mapping.get(zh_field, []):
                                if en_field in row:
                                    return row[en_field]
                            
                            return None
                        
                        # 准备创建或更新的数据
                        data = {
                            'material': material,
                            'process': process
                        }
                        
                        # 设置其他字段
                        fatigue_method = get_field_value(row, '测试类型')
                        if fatigue_method is not None and not pd.isna(fatigue_method):
                            data['fatigue_method'] = str(fatigue_method)
                        
                        stress_ratio = safe_float(get_field_value(row, '应力比'))
                        if stress_ratio is not None:
                            data['stress_ratio'] = stress_ratio
                        
                        stress_range = safe_float(get_field_value(row, '应力幅'))
                        if stress_range is not None:
                            data['stress_range'] = stress_range
                        
                        mean_stress = safe_float(get_field_value(row, '平均应力'))
                        if mean_stress is not None:
                            data['mean_stress'] = mean_stress
                        
                        loading_frequency = safe_float(get_field_value(row, '加载频率'))
                        if loading_frequency is not None:
                            data['loading_frequency'] = loading_frequency
                        
                        environment_temp = safe_float(get_field_value(row, '环境温度'))
                        if environment_temp is not None:
                            data['environment_temp'] = environment_temp
                        
                        fatigue_life = safe_float(get_field_value(row, '疲劳寿命'))
                        if fatigue_life is not None:
                            data['fatigue_life'] = fatigue_life
                        
                        fatigue_limit = safe_float(get_field_value(row, '疲劳极限'))
                        if fatigue_limit is not None:
                            data['fatigue_limit'] = fatigue_limit
                        
                        # 日志记录每行的数据，用于调试
                        logger.debug("Processed fatigue import row %s", idx + 2)
                        
                        # 如果有疲劳测试ID，尝试更新，否则创建新记录
                        fatigue_id_value = get_field_value(row, '疲劳测试ID')
                        if fatigue_id_value is not None and not pd.isna(fatigue_id_value):
                            try:
                                fatigue_id = int(fatigue_id_value)
                                # 检查ID是否存在
                                if FatTest.objects.filter(fatigue_id=fatigue_id).exists():
                                    # ID已存在，创建新记录（使用自增ID）
                                    new_record = FatTest.objects.create(**data)
                                    logger.info(f"ID={fatigue_id}已存在，创建新记录(自增ID): ID={new_record.fatigue_id}")
                                    auto_increment_count += 1
                                else:
                                    # 手动设置ID创建新记录
                                    data['fatigue_id'] = fatigue_id
                                    FatTest.objects.create(**data)
                                    logger.info(f"创建新记录，使用指定ID={fatigue_id}")
                            except (ValueError, TypeError):
                                error_records.append({
                                    "row": idx+2,
                                    "error": "疲劳测试ID必须为整数"
                                })
                                continue
                        else:
                            # 创建新记录
                            new_record = FatTest.objects.create(**data)
                            logger.info(f"创建新记录: ID={new_record.fatigue_id}")
                            auto_increment_count += 1
                        
                        success_count += 1
                    except Exception as e:
                        logger.error(f"处理第{idx+2}行时出错: {str(e)}")
                        error_records.append({
                            "row": idx+2,
                            "error": str(e)
                        })
            
            # 返回导入结果
            return Response({
                "success": True,
                "success_count": success_count,
                "auto_increment_count": auto_increment_count,
                "error_count": len(error_records),
                "errors": error_records[:10]  # 只返回前10条错误记录，避免响应体过大
            })
        except Exception as e:
            logger.error(f"导入疲劳测试数据时发生错误: {str(e)}")
            return Response({
                "success": False,
                "detail": f"导入失败: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class IrrConditionViewSet(viewsets.ModelViewSet):
    """辐照条件视图集"""
    queryset = IrrCondition.objects.all().order_by('-modify_time')
    serializer_class = IrrConditionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['irradiat_type', 'irradiat_id']
    filterset_fields = ['irradiat_type', 'irradiat_id']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """重写get_queryset方法以支持更灵活的查询"""
        queryset = super().get_queryset()
        
        # 获取搜索参数
        search_query = self.request.query_params.get('search', '')
        irradiat_id = self.request.query_params.get('irradiat_id')
        irradiat_type = self.request.query_params.get('irradiat_type')
        
        # 应用基本过滤条件
        if search_query:
            queryset = queryset.filter(
                Q(irradiat_type__icontains=search_query) |
                Q(irradiat_id__icontains=search_query)
            )
        
        if irradiat_id:
            queryset = queryset.filter(irradiat_id=irradiat_id)
            
        if irradiat_type:
            queryset = queryset.filter(irradiat_type__icontains=irradiat_type)
            
        return queryset

    @action(detail=False, methods=['post'])
    def import_data(self, request):
        """导入辐照条件数据"""
        try:
            file = request.FILES.get('file')
            if not file:
                return Response({"detail": "请选择一个文件"}, status=status.HTTP_400_BAD_REQUEST)
            
            # 根据文件扩展名选择合适的方法读取数据
            file_extension = str(file).split('.')[-1].lower()
            try:
                if file_extension == 'csv':
                    # 尝试不同编码方式读取CSV文件
                    try:
                        df = pd.read_csv(file, encoding='utf-8')
                    except UnicodeDecodeError:
                        df = pd.read_csv(file, encoding='gbk')
                elif file_extension in ('xlsx', 'xls'):
                    # 使用openpyxl引擎读取Excel文件
                    df = pd.read_excel(file, engine='openpyxl')
                else:
                    return Response({"detail": "不支持的文件格式，请上传.csv或.xlsx文件"}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                logger.error(f"文件读取错误: {str(e)}")
                return Response({"detail": f"文件读取错误: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
            
            # 打印列名便于调试
            logger.info(f"导入文件列名: {list(df.columns)}")
            logger.info("Irradiation-condition import parsed: rows=%s, columns=%s", len(df), len(df.columns))
            
            # 标准化列名映射 - 支持中英文列名
            column_mappings = {
                'irradiat_id': ['辐照ID', 'Irradiation ID', 'ID', 'id'],
                'irradiat_type': ['辐照类型', 'Irradiation Type'],
                'irradiat_energy': ['粒子能量', 'Particle Energy', 'Energy'],
                'irradiat_temp': ['辐照温度', 'Irradiation Temperature', 'Temperature'],
                'irradiat_dose': ['辐照剂量', 'Irradiation Dose', 'Dose'],
                'irradiat_fluence': ['辐照注量', 'Irradiation Fluence', 'Fluence'],
                'displac_damage': ['离位损伤', 'Displacement Damage', 'Damage']
            }
            
            # 尝试标准化列名
            normalized_columns = {}
            for model_field, possible_names in column_mappings.items():
                for col_name in possible_names:
                    if col_name in df.columns:
                        normalized_columns[col_name] = model_field
                        break
            
            # 如果找到了映射，重命名列
            if normalized_columns:
                df.rename(columns=normalized_columns, inplace=True)
                logger.info(f"标准化后的列名: {list(df.columns)}")
            
            # 处理导入数据
            success_count = 0
            auto_increment_count = 0
            error_records = []
            
            # 使用事务确保数据一致性
            with transaction.atomic():
                for idx, row in df.iterrows():
                    try:
                        # 准备数据
                        data = {}
                        
                        # 从标准化后的DataFrame提取数据
                        for field in ['irradiat_type', 'irradiat_energy', 'irradiat_temp', 
                                      'irradiat_dose', 'irradiat_fluence', 'displac_damage']:
                            if field in df.columns and pd.notna(row[field]):
                                # 数值字段需要转换
                                if field in ['irradiat_energy', 'irradiat_temp', 'irradiat_dose', 'displac_damage']:
                                    try:
                                        value = float(row[field])
                                        data[field] = value
                                    except (ValueError, TypeError):
                                        # 如果无法转换为浮点数，跳过此字段
                                        logger.warning(f"行 {idx+2}: 无法将 {field} 值 '{row[field]}' 转换为数值")
                                else:
                                    # 字符串字段直接使用
                                    data[field] = str(row[field])
                        
                        # 如果没有任何有效数据，跳过此行
                        if not data:
                            error_records.append({
                                "row": idx+2,
                                "error": "没有有效数据"
                            })
                            continue
                        
                        # 处理ID字段
                        irradiat_id = None
                        if 'irradiat_id' in df.columns and pd.notna(row['irradiat_id']):
                            try:
                                irradiat_id = int(row['irradiat_id'])
                            except (ValueError, TypeError):
                                error_records.append({
                                    "row": idx+2,
                                    "error": f"辐照ID '{row['irradiat_id']}' 必须是整数"
                                })
                                continue
                        
                        # 创建或更新记录
                        if irradiat_id is not None:
                            if IrrCondition.objects.filter(irradiat_id=irradiat_id).exists():
                                # ID已存在，创建新记录（使用自增ID）
                                new_record = IrrCondition.objects.create(**data)
                                logger.info(f"行 {idx+2}: ID={irradiat_id}已存在，创建新记录(自增ID): ID={new_record.irradiat_id}")
                                auto_increment_count += 1
                            else:
                                # 使用指定ID创建记录
                                data['irradiat_id'] = irradiat_id
                                IrrCondition.objects.create(**data)
                                logger.info(f"行 {idx+2}: 创建新记录，使用指定ID={irradiat_id}")
                        else:
                            # 使用自增ID创建记录
                            new_record = IrrCondition.objects.create(**data)
                            logger.info(f"行 {idx+2}: 创建新记录，使用自增ID: ID={new_record.irradiat_id}")
                            auto_increment_count += 1
                        
                        success_count += 1
                    except Exception as e:
                        logger.error(f"处理行 {idx+2} 时出错: {str(e)}")
                        error_records.append({
                            "row": idx+2,
                            "error": str(e)
                        })
            
            # 返回导入结果
            result = {
                "success": True,
                "message": f"导入完成：成功{success_count}条记录，失败{len(error_records)}条记录",
                "success_count": success_count,
                "auto_increment_count": auto_increment_count,
                "error_count": len(error_records),
                "errors": error_records[:10]  # 只返回前10条错误记录，避免响应体过大
            }
            
            if error_records:
                return Response(result, status=status.HTTP_207_MULTI_STATUS)
            else:
                return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"导入辐照条件数据时发生错误: {str(e)}")
            return Response({
                "success": False,
                "detail": f"导入失败: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def export_data(self, request):
        """导出辐照条件数据"""
        try:
            from django.utils import timezone
            from django.http import HttpResponse
            
            format_type = request.data.get('format', 'excel')
            property_ids = request.data.get('property_ids', [])
            
            # 获取要导出的数据
            queryset = self.get_queryset()
            if property_ids:
                queryset = queryset.filter(irradiat_id__in=property_ids)
            
            # 准备导出数据
            export_data = []
            for property in queryset:
                # 转换时间为本地时区
                entry_time = timezone.localtime(property.entry_time) if property.entry_time.tzinfo else timezone.localtime(timezone.make_aware(property.entry_time))
                modify_time = timezone.localtime(property.modify_time) if property.modify_time.tzinfo else timezone.localtime(timezone.make_aware(property.modify_time))
                
                export_data.append({
                    'Irradiation ID': property.irradiat_id,
                    'Irradiation Type': property.irradiat_type,
                    'Particle Energy': property.irradiat_energy,
                    'Irradiation Temperature': property.irradiat_temp,
                    'Irradiation Dose': property.irradiat_dose,
                    'Irradiation Fluence': property.irradiat_fluence,
                    'Displacement Damage': property.displac_damage,
                    'Entry Time': entry_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'Updated At': modify_time.strftime('%Y-%m-%d %H:%M:%S')
                })
            
            if not export_data:
                return Response({"detail": "没有数据可导出"}, status=status.HTTP_404_NOT_FOUND)
            
            # 将数据转换为DataFrame
            df = pd.DataFrame(export_data)
            
            # 根据format_type直接返回文件响应，而非通过REST框架的Response
            if format_type == 'excel':
                # 创建一个excel文件
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, sheet_name='Irradiation Conditions', index=False)
                
                # 设置response的headers和content_type
                output.seek(0)
                filename = f"irradiation_conditions_{timezone.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                response = HttpResponse(
                    output.getvalue(),
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                return response
            elif format_type == 'csv':
                # 创建一个CSV文件
                output = io.StringIO()
                df.to_csv(output, index=False)
                
                # 设置response的headers和content_type
                output.seek(0)
                filename = f"irradiation_conditions_{timezone.now().strftime('%Y%m%d_%H%M%S')}.csv"
                response = HttpResponse(
                    output.getvalue(),
                    content_type='text/csv'
                )
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                return response
            else:
                return Response({"detail": "不支持的导出格式"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"导出辐照条件数据时发生错误: {str(e)}")
            return Response({"detail": f"导出失败: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class MicrostructureEvolutionViewSet(viewsets.ModelViewSet):
    """微结构演化视图集"""
    queryset = MicrostructureEvolution.objects.all().order_by('-entry_time')
    serializer_class = MicrostructureEvolutionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['material__material_id', 'process__process_id', 'irradiat__irradiat_id']
    search_fields = ['microstructure_id']
    ordering_fields = ['entry_time', 'modify_time', 'he_bubble_diam', 'he_bubble_dens', 'swelling_rate', 'irradiat_hard']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """重写get_queryset方法以支持更灵活的查询"""
        queryset = super().get_queryset()
        
        # 获取查询参数
        material_id = self.request.query_params.get('material_id')
        process_id = self.request.query_params.get('process_id')
        irradiat_id = self.request.query_params.get('irradiat_id')
        
        # 获取范围查询参数
        he_bubble_diam_min = self.request.query_params.get('he_bubble_diam_min')
        he_bubble_diam_max = self.request.query_params.get('he_bubble_diam_max')
        he_bubble_dens_min = self.request.query_params.get('he_bubble_dens_min')
        he_bubble_dens_max = self.request.query_params.get('he_bubble_dens_max')
        swelling_rate_min = self.request.query_params.get('swelling_rate_min')
        swelling_rate_max = self.request.query_params.get('swelling_rate_max')
        irradiat_hard_min = self.request.query_params.get('irradiat_hard_min')
        irradiat_hard_max = self.request.query_params.get('irradiat_hard_max')
        
        # 定义一个安全过滤函数
        def safe_filter(queryset, field_name, op, value):
            """安全的过滤函数，避免非法输入"""
            try:
                if value is not None and value != '':
                    value = float(value)
                    filter_kwargs = {f'{field_name}__{op}': value}
                    queryset = queryset.filter(**filter_kwargs)
            except (ValueError, TypeError) as e:
                logger.warning(f"过滤字段 {field_name} 的值 {value} 无效: {str(e)}")
            return queryset
            
        # 基于关联ID过滤
        if material_id:
            queryset = queryset.filter(material__material_id=material_id)
        if process_id:
            queryset = queryset.filter(process__process_id=process_id)
        if irradiat_id:
            queryset = queryset.filter(irradiat__irradiat_id=irradiat_id)
            
        # 范围过滤
        queryset = safe_filter(queryset, 'he_bubble_diam', 'gte', he_bubble_diam_min)
        queryset = safe_filter(queryset, 'he_bubble_diam', 'lte', he_bubble_diam_max)
        queryset = safe_filter(queryset, 'he_bubble_dens', 'gte', he_bubble_dens_min)
        queryset = safe_filter(queryset, 'he_bubble_dens', 'lte', he_bubble_dens_max)
        queryset = safe_filter(queryset, 'swelling_rate', 'gte', swelling_rate_min)
        queryset = safe_filter(queryset, 'swelling_rate', 'lte', swelling_rate_max)
        queryset = safe_filter(queryset, 'irradiat_hard', 'gte', irradiat_hard_min)
        queryset = safe_filter(queryset, 'irradiat_hard', 'lte', irradiat_hard_max)
            
        return queryset

    def list(self, request, *args, **kwargs):
        """获取微结构演化列表"""
        try:
            logger.debug(f"List request params: {request.query_params}")
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                response_data = self.get_paginated_response(serializer.data)
                logger.debug(f"Paginated response data count: {len(serializer.data)}")
                return response_data
            
            serializer = self.get_serializer(queryset, many=True)
            response_data = {
                'results': serializer.data,
                'count': queryset.count()
            }
            logger.debug(f"Non-paginated response data count: {len(serializer.data)}")
            return Response(response_data)
        except Exception as e:
            logger.error(f"获取微结构演化列表失败: {str(e)}")
            return Response({'error': f'获取数据失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        """创建微结构演化记录"""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except serializers.ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"创建微结构演化记录失败: {str(e)}")
            return Response({'error': f'创建失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        """更新微结构演化记录"""
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        except serializers.ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"更新微结构演化记录失败: {str(e)}")
            return Response({'error': f'更新失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        """删除微结构演化记录"""
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error(f"删除微结构演化记录失败: {str(e)}")
            return Response({'error': f'删除失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], url_path='import')
    def import_data(self, request):
        """导入微结构演化数据"""
        try:
            if 'file' not in request.FILES:
                return Response({'error': '请选择要导入的文件'}, status=400)

            file = request.FILES['file']
            if not file.name.endswith(('.xls', '.xlsx')):
                return Response({'error': '只支持Excel文件格式'}, status=400)

            # 读取Excel文件
            try:
                # 尝试多种方式读取Excel文件
                try:
                    # 首先尝试使用对象类型读取ID列，便于后续处理
                    df = pd.read_excel(file, dtype={
                        'material_id': object,
                        'process_id': object,
                        'irradiat_id': object,
                        'he_bubble_diam': object,
                        'he_bubble_dens': object,
                        'swelling_rate': object,
                        'irradiat_hard': object
                    })
                except Exception:
                    # 如果上面的方法失败，尝试默认读取方式
                    logger.warning("使用对象类型读取失败，尝试使用默认类型读取")
                    df = pd.read_excel(file)
            except Exception as e:
                logger.error(f"Excel读取错误: {str(e)}")
                return Response({'error': f'Excel文件读取失败: {str(e)}'}, status=400)

            # Normalize current English exports and legacy Chinese exports to model fields.
            column_aliases = {
                'Microstructure ID': 'microstructure_id',
                '微结构ID': 'microstructure_id',
                'Material ID': 'material_id',
                '材料ID': 'material_id',
                'Process ID': 'process_id',
                '工艺ID': 'process_id',
                'Irradiation ID': 'irradiat_id',
                '辐照ID': 'irradiat_id',
                'Helium Bubble Diameter': 'he_bubble_diam',
                '氦泡直径': 'he_bubble_diam',
                'Helium Bubble Density': 'he_bubble_dens',
                '氦泡密度': 'he_bubble_dens',
                'Swelling Rate': 'swelling_rate',
                '肿胀率': 'swelling_rate',
                'Irradiation Hardening': 'irradiat_hard',
                '辐照硬化量': 'irradiat_hard',
            }
            df.rename(
                columns=lambda column: column_aliases.get(str(column).strip(), str(column).strip()),
                inplace=True,
            )

            # 验证必需列
            required_columns = ['material_id', 'process_id', 'irradiat_id']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                return Response({
                    'error': f'Excel文件缺少必需列: {", ".join(missing_columns)}'
                }, status=400)
            
            success_count = 0
            errors = []
            skip_rows = []
            
            # 第一次遍历：验证所有数据
            for index, row in df.iterrows():
                row_errors = []
                
                # 检查必填字段
                for field in required_columns:
                    value = row.get(field)
                    if pd.isna(value) or str(value).strip() == '':
                        row_errors.append(f"{field} 不能为空")
                        continue
                    
                    # 尝试验证ID格式
                    try:
                        # 统一处理浮点数、字符串等格式的ID
                        id_value = str(value).strip()
                        if '.' in id_value:
                            int(float(id_value))  # 检查是否可以转换
                        else:
                            int(id_value)  # 检查是否可以转换
                    except ValueError:
                        row_errors.append(f"{field} '{value}' 必须是整数")
                
                # 检查数值字段
                numeric_fields = ['he_bubble_diam', 'he_bubble_dens', 'swelling_rate', 'irradiat_hard']
                for field in numeric_fields:
                    value = row.get(field)
                    if not pd.isna(value) and str(value).strip() != '':
                        try:
                            float_val = float(str(value).strip())
                            if float_val < 0:
                                row_errors.append(f"{field} 不能为负数")
                        except ValueError:
                            row_errors.append(f"{field} '{value}' 必须是数字")
                
                # 如果有错误，添加到总错误列表并标记跳过该行
                if row_errors:
                    errors.append(f"第{index + 2}行: {'; '.join(row_errors)}")
                    skip_rows.append(index)
            
            # 如果所有行都有错误，直接返回错误报告
            if len(skip_rows) == len(df):
                return Response({
                    'success': False,
                    'message': '所有数据都存在格式问题，无法导入',
                    'success_count': 0,
                    'error_count': len(errors),
                    'errors': errors[:10] if len(errors) > 10 else errors
                })
            
            # 开启事务
            with transaction.atomic():
                # 第二次遍历：处理有效数据
                for index, row in df.iterrows():
                    # 跳过已知有问题的行
                    if index in skip_rows:
                        continue
                    
                    try:
                        # 处理材料ID
                        material_id_str = str(row['material_id']).strip()
                        try:
                            # 转换为整数
                            if '.' in material_id_str:
                                material_id = int(float(material_id_str))
                            else:
                                material_id = int(material_id_str)
                                
                            try:
                                material = Material.objects.get(material_id=material_id)
                            except Material.DoesNotExist:
                                errors.append(f"第{index + 2}行: 材料ID {material_id} 不存在")
                                continue
                        except Exception as e:
                            errors.append(f"第{index + 2}行: 处理材料ID '{material_id_str}' 时出错: {str(e)}")
                            continue
                        
                        # 处理工艺ID
                        process_id_str = str(row['process_id']).strip()
                        try:
                            # 转换为整数
                            if '.' in process_id_str:
                                process_id = int(float(process_id_str))
                            else:
                                process_id = int(process_id_str)
                                
                            try:
                                process = Process.objects.get(process_id=process_id)
                            except Process.DoesNotExist:
                                errors.append(f"第{index + 2}行: 工艺ID {process_id} 不存在")
                                continue
                        except Exception as e:
                            errors.append(f"第{index + 2}行: 处理工艺ID '{process_id_str}' 时出错: {str(e)}")
                            continue
                        
                        # 处理辐照ID
                        irradiat_id_str = str(row['irradiat_id']).strip()
                        try:
                            # 转换为整数
                            if '.' in irradiat_id_str:
                                irradiat_id = int(float(irradiat_id_str))
                            else:
                                irradiat_id = int(irradiat_id_str)
                                
                            try:
                                irradiat = IrrCondition.objects.get(irradiat_id=irradiat_id)
                            except IrrCondition.DoesNotExist:
                                errors.append(f"第{index + 2}行: 辐照ID {irradiat_id} 不存在")
                                continue
                        except Exception as e:
                            errors.append(f"第{index + 2}行: 处理辐照ID '{irradiat_id_str}' 时出错: {str(e)}")
                            continue
                        
                        # 安全处理数值字段
                        microstructure_data = {
                            'material': material,
                            'process': process,
                            'irradiat': irradiat
                        }
                        
                        # 处理可选的数值字段，任何转换错误都会将字段值设为None而不是报错
                        numeric_fields = ['he_bubble_diam', 'he_bubble_dens', 'swelling_rate', 'irradiat_hard']
                        for field in numeric_fields:
                            try:
                                value = row.get(field)
                                if pd.isna(value) or str(value).strip() == '':
                                    microstructure_data[field] = None
                                else:
                                    float_val = float(str(value).strip())
                                    microstructure_data[field] = float_val if float_val >= 0 else None
                            except (ValueError, TypeError):
                                # 如果转换失败，设置为None
                                microstructure_data[field] = None
                        
                        # 创建或更新记录
                        obj, created = MicrostructureEvolution.objects.update_or_create(
                            material=material,
                            process=process,
                            irradiat=irradiat,
                            defaults=microstructure_data
                        )
                        success_count += 1
                    
                    except Exception as e:
                        logger.error(f"导入第{index + 2}行数据时出错: {str(e)}")
                        errors.append(f"第{index + 2}行: {str(e)}")

            # 返回导入结果
            response_data = {
                'success': success_count > 0,  # 只要有成功的记录就视为成功
                'message': f'成功导入 {success_count} 条记录' + (f', 失败 {len(errors)} 条' if errors else ''),
                'success_count': success_count,
                'error_count': len(errors),
                'errors': errors[:10] if errors else []  # 只返回前10个错误
            }
            
            return Response(response_data)

        except Exception as e:
            logger.error(f"导入数据时发生错误: {str(e)}")
            return Response({
                'error': f'导入失败: {str(e)}',
                'success': False
            }, status=500)

    def _safe_float(self, value):
        """安全转换数值类型"""
        if pd.isna(value) or value == '' or value is None:
            return None
        try:
            # 确保字符串格式
            if isinstance(value, str):
                value = value.strip()
            
            # 转换为浮点数
            float_val = float(value)
            
            # 检查是否为有限数值
            if not math.isfinite(float_val):
                return None
                
            # 如果是负数，返回None
            if float_val < 0:
                return None
                
            return float_val
        except (ValueError, TypeError):
            # 如果是字符串，尝试清理并再次转换
            if isinstance(value, str):
                try:
                    # 移除可能的非数字字符，但保留小数点和负号
                    cleaned = ''.join(c for c in value if c.isdigit() or c in '.-')
                    if not cleaned:
                        return None
                    
                    float_val = float(cleaned)
                    # 检查负数
                    if float_val < 0:
                        return None
                    return float_val
                except (ValueError, TypeError):
                    pass
            return None

    @action(detail=False, methods=['post'])
    def export_data(self, request):
        """导出微结构演化数据"""
        try:
            format_type = request.data.get('format', 'excel')
            property_ids = request.data.get('property_ids', [])
            
            # 获取要导出的数据
            queryset = self.get_queryset()
            if property_ids:
                queryset = queryset.filter(microstructure_id__in=property_ids)
            
            # 准备导出数据
            export_data = []
            for ms in queryset:
                # 转换时间为本地时区
                entry_time = timezone.localtime(ms.entry_time) if ms.entry_time.tzinfo else timezone.localtime(timezone.make_aware(ms.entry_time))
                modify_time = timezone.localtime(ms.modify_time) if ms.modify_time.tzinfo else timezone.localtime(timezone.make_aware(ms.modify_time))
                
                property_data = {
                    'Microstructure ID': ms.microstructure_id,
                    'Material ID': ms.material.material_id,
                    'Material Name': ms.material.material_name,
                    'Process ID': ms.process.process_id,
                    'Irradiation ID': ms.irradiat.irradiat_id,
                    'Helium Bubble Diameter': ms.he_bubble_diam,
                    'Helium Bubble Density': ms.he_bubble_dens,
                    'Swelling Rate': ms.swelling_rate,
                    'Irradiation Hardening': ms.irradiat_hard,
                    'Entry Time': entry_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'Updated At': modify_time.strftime('%Y-%m-%d %H:%M:%S')
                }
                export_data.append(property_data)
            
            # 创建DataFrame
            df = pd.DataFrame(export_data)
            
            # 根据格式类型导出文件
            if format_type == 'csv':
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="microstructure_evolution.csv"'
                df.to_csv(response, index=False, encoding='utf-8-sig')
            else:  # excel
                response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                response['Content-Disposition'] = 'attachment; filename="microstructure_evolution.xlsx"'
                with pd.ExcelWriter(response, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Microstructure Evolution')
            
            return response
            
        except Exception as e:
            logger.error(f"导出微结构演化数据失败: {str(e)}")
            return Response({'error': f'导出失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class EmbrittlementViewSet(viewsets.ModelViewSet):
    """辐照脆化视图集"""
    queryset = Embrittlement.objects.all().order_by('-entry_time')
    serializer_class = EmbrittlementSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['material__material_id', 'process__process_id', 'irradiat__irradiat_id']
    search_fields = ['embrittlement_id']
    ordering_fields = ['entry_time', 'modify_time', 'dbtt', 'dbtt_difference']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # 按材料ID筛选
        material_id = self.request.query_params.get('material_id')
        if material_id:
            queryset = queryset.filter(material__material_id=material_id)
        
        # 按工艺ID筛选
        process_id = self.request.query_params.get('process_id')
        if process_id:
            queryset = queryset.filter(process__process_id=process_id)
        
        # 按辐照ID筛选
        irradiat_id = self.request.query_params.get('irradiat_id')
        if irradiat_id:
            queryset = queryset.filter(irradiat__irradiat_id=irradiat_id)
        
        # 数值字段范围筛选
        def safe_filter(queryset, field_name, op, value):
            try:
                value = float(value)
                filter_kwargs = {f"{field_name}__{op}": value}
                return queryset.filter(**filter_kwargs)
            except (ValueError, TypeError):
                return queryset
        
        # 韧脆转变温度筛选
        dbtt_min = self.request.query_params.get('dbtt_min')
        dbtt_max = self.request.query_params.get('dbtt_max')
        if dbtt_min:
            queryset = safe_filter(queryset, 'dbtt', 'gte', dbtt_min)
        if dbtt_max:
            queryset = safe_filter(queryset, 'dbtt', 'lte', dbtt_max)
        
        # 韧脆转变温度变化筛选
        dbtt_diff_min = self.request.query_params.get('dbtt_difference_min')
        dbtt_diff_max = self.request.query_params.get('dbtt_difference_max')
        if dbtt_diff_min:
            queryset = safe_filter(queryset, 'dbtt_difference', 'gte', dbtt_diff_min)
        if dbtt_diff_max:
            queryset = safe_filter(queryset, 'dbtt_difference', 'lte', dbtt_diff_max)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'])
    def batch_delete(self, request):
        """批量删除辐照脆化记录"""
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'error': '没有提供要删除的ID'}, status=status.HTTP_400_BAD_REQUEST)
            
        deleted_count = 0
        try:
            deleted_count, _ = Embrittlement.objects.filter(embrittlement_id__in=ids).delete()
            return Response({'message': f'成功删除{deleted_count}条记录'})
        except Exception as e:
            logger.error(f"批量删除辐照脆化记录时出错: {str(e)}")
            return Response({'error': f'删除失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def import_data(self, request):
        """导入辐照脆化数据"""
        if 'file' not in request.FILES:
            return Response({'error': '没有上传文件'}, status=status.HTTP_400_BAD_REQUEST)
            
        file_obj = request.FILES['file']
        
        # 检查文件类型
        file_ext = os.path.splitext(file_obj.name)[1].lower()
        if file_ext not in ['.csv', '.xlsx', '.xls']:
            return Response({'error': '不支持的文件格式，请上传CSV或Excel文件'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            if file_ext == '.csv':
                df = pd.read_csv(file_obj, encoding='utf-8')
            else:
                df = pd.read_excel(file_obj)
            
            # 记录导入文件信息
            logger.info(f"开始导入辐照脆化数据, 文件: {file_obj.name}, 行数: {len(df)}")
            
            # 处理可能的列名映射
            column_map = {
                '材料ID': 'material_id',
                'Material ID': 'material_id',
                '工艺ID': 'process_id',
                'Process ID': 'process_id',
                '辐照ID': 'irradiat_id',
                'Irradiation ID': 'irradiat_id',
                '韧脆转变温度': 'dbtt',
                'DBTT': 'dbtt',
                'Ductile-to-Brittle Transition Temperature': 'dbtt',
                '韧脆转变温度变化': 'dbtt_difference',
                'DBTT Change': 'dbtt_difference',
                'Ductile-to-Brittle Transition Temperature Change': 'dbtt_difference'
            }
            
            # 规范化列名
            df.rename(columns={k: v for k, v in column_map.items() if k in df.columns}, inplace=True)
            
            # 记录列名
            logger.info(f"导入文件列名: {list(df.columns)}")
            
            # 必需的列
            required_columns = ['material_id', 'process_id', 'irradiat_id']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                logger.error(f"文件缺少必需的列: {missing_columns}")
                return Response({
                    'error': f'文件缺少必需的列: {", ".join(missing_columns)}',
                    'required_columns': required_columns
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 处理数据
            success_count = 0
            errors = []
            
            for index, row in df.iterrows():
                try:
                    # 记录当前处理的行
                    logger.debug("Processing embrittlement import row %s", index + 2)
                    
                    # 处理材料ID
                    material_id_str = str(row['material_id']).strip()
                    try:
                        material_id = int(float(material_id_str)) if '.' in material_id_str else int(material_id_str)
                        try:
                            material = Material.objects.get(material_id=material_id)
                        except Material.DoesNotExist:
                            error_msg = f"第{index + 2}行: 材料ID {material_id} 不存在"
                            logger.error(error_msg)
                            errors.append(error_msg)
                            continue
                    except Exception as e:
                        error_msg = f"第{index + 2}行: 处理材料ID '{material_id_str}' 时出错: {str(e)}"
                        logger.error(error_msg)
                        errors.append(error_msg)
                        continue
                    
                    # 处理工艺ID
                    process_id_str = str(row['process_id']).strip()
                    try:
                        process_id = int(float(process_id_str)) if '.' in process_id_str else int(process_id_str)
                        try:
                            process = Process.objects.get(process_id=process_id)
                        except Process.DoesNotExist:
                            error_msg = f"第{index + 2}行: 工艺ID {process_id} 不存在"
                            logger.error(error_msg)
                            errors.append(error_msg)
                            continue
                    except Exception as e:
                        error_msg = f"第{index + 2}行: 处理工艺ID '{process_id_str}' 时出错: {str(e)}"
                        logger.error(error_msg)
                        errors.append(error_msg)
                        continue
                    
                    # 处理辐照ID
                    irradiat_id_str = str(row['irradiat_id']).strip()
                    try:
                        irradiat_id = int(float(irradiat_id_str)) if '.' in irradiat_id_str else int(irradiat_id_str)
                        try:
                            irradiat = IrrCondition.objects.get(irradiat_id=irradiat_id)
                        except IrrCondition.DoesNotExist:
                            error_msg = f"第{index + 2}行: 辐照ID {irradiat_id} 不存在"
                            logger.error(error_msg)
                            errors.append(error_msg)
                            continue
                    except Exception as e:
                        error_msg = f"第{index + 2}行: 处理辐照ID '{irradiat_id_str}' 时出错: {str(e)}"
                        logger.error(error_msg)
                        errors.append(error_msg)
                        continue
                    
                    # 安全处理数值字段
                    defaults = {}
                    
                    # 处理可选的数值字段
                    numeric_fields = ['dbtt', 'dbtt_difference']
                    for field in numeric_fields:
                        try:
                            value = row.get(field)
                            if pd.isna(value) or str(value).strip() == '':
                                defaults[field] = None
                            else:
                                defaults[field] = float(str(value).strip())
                        except (ValueError, TypeError):
                            defaults[field] = None
                    
                    # 创建或更新记录 - 修改为更明确的创建和更新逻辑
                    try:
                        # 先尝试查找现有记录
                        existing = Embrittlement.objects.filter(
                            material=material,
                            process=process,
                            irradiat=irradiat
                        ).first()
                        
                        if existing:
                            # 更新现有记录
                            for field, value in defaults.items():
                                setattr(existing, field, value)
                            existing.save()
                            logger.info(f"第{index + 2}行: 更新记录 ID={existing.embrittlement_id}")
                        else:
                            # 创建新记录
                            new_record = Embrittlement.objects.create(
                                material=material,
                                process=process,
                                irradiat=irradiat,
                                **defaults
                            )
                            logger.info(f"第{index + 2}行: 创建新记录 ID={new_record.embrittlement_id}")
                        
                        success_count += 1
                    except Exception as e:
                        error_msg = f"第{index + 2}行: 保存记录时出错: {str(e)}"
                        logger.error(error_msg)
                        errors.append(error_msg)
                        continue
                
                except Exception as e:
                    error_msg = f"导入第{index + 2}行数据时出错: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)
            
            # 返回导入结果
            response_data = {
                'success': success_count > 0,
                'message': f'成功导入 {success_count} 条记录' + (f', 失败 {len(errors)} 条' if errors else ''),
                'success_count': success_count,
                'error_count': len(errors),
                'errors': errors[:10] if errors else []
            }
            
            logger.info(f"辐照脆化数据导入完成: 成功={success_count}, 失败={len(errors)}")
            return Response(response_data)
            
        except Exception as e:
            error_msg = f"导入数据时发生错误: {str(e)}"
            logger.error(error_msg)
            return Response({
                'error': error_msg,
                'success': False
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def range_query(self, request):
        """辐照脆化数据范围查询"""
        # 获取查询参数
        dbtt_min = request.data.get('dbtt_min')
        dbtt_max = request.data.get('dbtt_max')
        dbtt_diff_min = request.data.get('dbtt_difference_min')
        dbtt_diff_max = request.data.get('dbtt_difference_max')
        material_id = request.data.get('material_id')
        process_id = request.data.get('process_id')
        irradiat_id = request.data.get('irradiat_id')
        
        # 开始查询
        queryset = self.get_queryset()
        
        # 应用筛选条件
        if material_id:
            queryset = queryset.filter(material__material_id=material_id)
        if process_id:
            queryset = queryset.filter(process__process_id=process_id)
        if irradiat_id:
            queryset = queryset.filter(irradiat__irradiat_id=irradiat_id)
            
        # 应用数值范围筛选
        def safe_filter(queryset, field_name, op, value):
            try:
                value = float(value)
                filter_kwargs = {f"{field_name}__{op}": value}
                return queryset.filter(**filter_kwargs)
            except (ValueError, TypeError):
                return queryset
        
        # 韧脆转变温度范围筛选
        if dbtt_min is not None:
            queryset = safe_filter(queryset, 'dbtt', 'gte', dbtt_min)
        if dbtt_max is not None:
            queryset = safe_filter(queryset, 'dbtt', 'lte', dbtt_max)
            
        # 韧脆转变温度变化范围筛选
        if dbtt_diff_min is not None:
            queryset = safe_filter(queryset, 'dbtt_difference', 'gte', dbtt_diff_min)
        if dbtt_diff_max is not None:
            queryset = safe_filter(queryset, 'dbtt_difference', 'lte', dbtt_diff_max)
        
        # 分页处理
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def export_data(self, request):
        """导出辐照脆化数据"""
        try:
            format_type = request.data.get('format', 'excel')
            property_ids = request.data.get('property_ids', [])
            
            # 获取要导出的数据
            queryset = self.get_queryset()
            if property_ids:
                queryset = queryset.filter(embrittlement_id__in=property_ids)
            
            # 准备导出数据
            export_data = []
            for item in queryset:
                # 转换时间为本地时区
                entry_time = timezone.localtime(item.entry_time) if item.entry_time.tzinfo else timezone.localtime(timezone.make_aware(item.entry_time))
                modify_time = timezone.localtime(item.modify_time) if item.modify_time.tzinfo else timezone.localtime(timezone.make_aware(item.modify_time))
                
                property_data = {
                    'Irradiation Embrittlement ID': item.embrittlement_id,
                    'Material ID': item.material.material_id,
                    'Material Name': item.material.material_name,
                    'Process ID': item.process.process_id,
                    'Irradiation ID': item.irradiat.irradiat_id,
                    'DBTT': item.dbtt,
                    'DBTT Change': item.dbtt_difference,
                    'Entry Time': entry_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'Updated At': modify_time.strftime('%Y-%m-%d %H:%M:%S')
                }
                export_data.append(property_data)
            
            # 创建DataFrame
            df = pd.DataFrame(export_data)
            
            # 根据格式类型导出文件
            if format_type == 'csv':
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="irradiation_embrittlement.csv"'
                df.to_csv(response, index=False, encoding='utf-8-sig')
            else:  # excel
                response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                response['Content-Disposition'] = 'attachment; filename="irradiation_embrittlement.xlsx"'
                with pd.ExcelWriter(response, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Irradiation Embrittlement')
            
            return response
            
        except Exception as e:
            logger.error(f"导出辐照脆化数据失败: {str(e)}")
            return Response({'error': f'导出失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class IrrCreepViewSet(viewsets.ModelViewSet):
    """辐照蠕变视图集"""
    queryset = IrrCreep.objects.all().order_by('-entry_time')
    serializer_class = IrrCreepSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['material__material_id', 'process__process_id', 'irradiat__irradiat_id']
    search_fields = ['ircreep_id']
    ordering_fields = ['entry_time', 'modify_time', 'ircreep_temp', 'ircreep_time', 'irinitial_stress', 'ircreep_rate']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # 材料ID和工艺ID过滤
        material_id = self.request.query_params.get('material_id')
        if material_id:
            queryset = queryset.filter(material__material_id=material_id)
            
        process_id = self.request.query_params.get('process_id')
        if process_id:
            queryset = queryset.filter(process__process_id=process_id)
            
        irradiat_id = self.request.query_params.get('irradiat_id')
        if irradiat_id:
            queryset = queryset.filter(irradiat__irradiat_id=irradiat_id)

        # 使用安全过滤函数处理数值范围过滤
        def safe_filter(queryset, field_name, op, value):
            """安全过滤函数，处理ValueError和TypeError异常"""
            if not value:
                return queryset
            try:
                value = float(value)
                filter_kwargs = {f"{field_name}__{op}": value}
                return queryset.filter(**filter_kwargs)
            except (ValueError, TypeError):
                return queryset
        
        # 处理数值字段范围过滤
        range_fields = {
            'ircreep_temp': ['ircreep_temp_min', 'ircreep_temp_max'],
            'ircreep_time': ['ircreep_time_min', 'ircreep_time_max'],
            'irinitial_stress': ['irinitial_stress_min', 'irinitial_stress_max'],
            'ircreep_rate': ['ircreep_rate_min', 'ircreep_rate_max'],
            'ircreep_limit': ['ircreep_limit_min', 'ircreep_limit_max'],
            'ircreep_rupture_strength': ['ircreep_rupture_strength_min', 'ircreep_rupture_strength_max'],
            'irrupture_time': ['irrupture_time_min', 'irrupture_time_max'],
            'irrupture_strength_limit': ['irrupture_strength_limit_min', 'irrupture_strength_limit_max'],
            'irpercentage_elongation': ['irpercentage_elongation_min', 'irpercentage_elongation_max']
        }
        
        for field, [min_param, max_param] in range_fields.items():
            min_value = self.request.query_params.get(min_param)
            max_value = self.request.query_params.get(max_param)
            queryset = safe_filter(queryset, field, 'gte', min_value)
            queryset = safe_filter(queryset, field, 'lte', max_value)
            
        return queryset

    @action(detail=False, methods=['post'])
    def import_data(self, request):
        """导入辐照蠕变数据"""
        if 'file' not in request.FILES:
            return Response({'error': '请选择Excel文件'}, status=status.HTTP_400_BAD_REQUEST)
            
        file = request.FILES['file']
        
        # 检查文件类型
        if not file.name.endswith(('.xlsx', '.xls')):
            return Response({'error': '只支持Excel文件格式'}, status=status.HTTP_400_BAD_REQUEST)
            
        # 检查文件大小
        if file.size > 10 * 1024 * 1024:  # 10MB
            return Response({'error': '文件大小不能超过10MB'}, status=status.HTTP_400_BAD_REQUEST)
            
        success_count = 0
        error_count = 0
        errors = []
        
        try:
            # 读取Excel文件
            df = pd.read_excel(file)

            # Normalize current English exports while retaining all legacy aliases.
            column_aliases = {
                'Material ID': 'material_id',
                '材料ID': 'material_id',
                'Process ID': 'process_id',
                '工艺ID': 'process_id',
                'Irradiation ID': 'irradiat_id',
                '辐照ID': 'irradiat_id',
                'Experiment Temperature (deg C)': 'ircreep_temp',
                'Experiment Temperature': 'ircreep_temp',
                '实验温度(℃)': 'ircreep_temp',
                '实验温度': 'ircreep_temp',
                'Experiment Time (h)': 'ircreep_time',
                'Experiment Time': 'ircreep_time',
                '实验时间(h)': 'ircreep_time',
                '实验时间': 'ircreep_time',
                'Initial Stress (MPa)': 'irinitial_stress',
                'Initial Stress': 'irinitial_stress',
                '初始应力(MPa)': 'irinitial_stress',
                '初始应力': 'irinitial_stress',
                'Steady-State Creep Rate': 'ircreep_rate',
                '稳态蠕变速率': 'ircreep_rate',
                'Creep Limit': 'ircreep_limit',
                '蠕变极限': 'ircreep_limit',
                'Creep Rupture Strength (MPa)': 'ircreep_rupture_strength',
                'Creep Rupture Strength': 'ircreep_rupture_strength',
                '蠕变持久强度(MPa)': 'ircreep_rupture_strength',
                '蠕变持久强度': 'ircreep_rupture_strength',
                'Rupture Time (h)': 'irrupture_time',
                'Rupture Time': 'irrupture_time',
                '断裂时间(h)': 'irrupture_time',
                '断裂时间': 'irrupture_time',
                'Rupture Strength Limit (MPa)': 'irrupture_strength_limit',
                'Rupture Strength Limit': 'irrupture_strength_limit',
                '持久强度极限(MPa)': 'irrupture_strength_limit',
                '持久强度极限': 'irrupture_strength_limit',
                'Elongation After Fracture (%)': 'irpercentage_elongation',
                'Elongation After Fracture': 'irpercentage_elongation',
                '断后伸长率(%)': 'irpercentage_elongation',
                '断后伸长率': 'irpercentage_elongation',
            }
            df.rename(
                columns=lambda column: column_aliases.get(str(column).strip(), str(column).strip()),
                inplace=True,
            )
            
            # 记录所有错误
            for index, row in df.iterrows():
                try:
                    # 转换为字典
                    data = {
                        'material_id': self._safe_convert(row.get('材料ID', row.get('material_id'))),
                        'process_id': self._safe_convert(row.get('工艺ID', row.get('process_id'))),
                        'irradiat_id': self._safe_convert(row.get('辐照ID', row.get('irradiat_id'))),
                        'ircreep_temp': self._safe_float(row.get('实验温度', row.get('ircreep_temp'))),
                        'ircreep_time': self._safe_float(row.get('实验时间', row.get('ircreep_time'))),
                        'irinitial_stress': self._safe_float(row.get('初始应力', row.get('irinitial_stress'))),
                        'ircreep_rate': self._safe_float(row.get('稳态蠕变速率', row.get('ircreep_rate'))),
                        'ircreep_limit': self._safe_float(row.get('蠕变极限', row.get('ircreep_limit'))),
                        'ircreep_rupture_strength': self._safe_float(row.get('蠕变持久强度', row.get('ircreep_rupture_strength'))),
                        'irrupture_time': self._safe_float(row.get('断裂时间', row.get('irrupture_time'))),
                        'irrupture_strength_limit': self._safe_float(row.get('持久强度极限', row.get('irrupture_strength_limit'))),
                        'irpercentage_elongation': self._safe_float(row.get('断后伸长率', row.get('irpercentage_elongation')))
                    }
                    
                    # 验证和保存数据
                    serializer = self.get_serializer(data=data)
                    if serializer.is_valid():
                        serializer.save()
                        success_count += 1
                    else:
                        error_message = f"第{index + 2}行: {serializer.errors}"
                        errors.append(error_message)
                        error_count += 1
                        
                except Exception as e:
                    errors.append(f"第{index + 2}行: {str(e)}")
                    error_count += 1
                    
            return Response({
                'success': True,
                'success_count': success_count,
                'error_count': error_count,
                'errors': errors
            })
            
        except Exception as e:
            logger.error(f"导入失败: {str(e)}")
            return Response({
                'success': False,
                'error': f'导入失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    def _safe_convert(self, value):
        """安全转换可能是字符串或数字的ID值"""
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return str(value)
            
    def _safe_float(self, value):
        """安全转换浮点数"""
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
            
    @action(detail=False, methods=['post'])
    def export_data(self, request):
        """导出辐照蠕变数据"""
        from django.utils import timezone
        
        property_ids = request.data.get('property_ids', [])
        format_type = request.data.get('format', 'excel')
        
        if format_type != 'excel':
            return Response({
                'error': '目前只支持Excel格式导出'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        # 获取要导出的数据
        if property_ids:
            queryset = self.queryset.filter(ircreep_id__in=property_ids)
        else:
            queryset = self.get_queryset()
            
        # 创建DataFrame
        data = []
        for item in queryset:
            # 转换时间为本地时区
            entry_time = timezone.localtime(item.entry_time) if item.entry_time.tzinfo else timezone.localtime(timezone.make_aware(item.entry_time))
            modify_time = timezone.localtime(item.modify_time) if item.modify_time.tzinfo else timezone.localtime(timezone.make_aware(item.modify_time))
            
            data.append({
                'Irradiation Creep ID': item.ircreep_id,
                'Material ID': item.material.material_id,
                'Material Name': item.material.material_name,
                'Process ID': item.process.process_id,
                'Process Name': item.process.fabrication,
                'Irradiation ID': item.irradiat.irradiat_id,
                'Irradiation Type': item.irradiat.irradiat_type,
                'Experiment Temperature (deg C)': item.ircreep_temp,
                'Experiment Time (h)': item.ircreep_time,
                'Initial Stress (MPa)': item.irinitial_stress,
                'Steady-State Creep Rate': item.ircreep_rate,
                'Creep Limit': item.ircreep_limit,
                'Creep Rupture Strength (MPa)': item.ircreep_rupture_strength,
                'Rupture Time (h)': item.irrupture_time,
                'Rupture Strength Limit (MPa)': item.irrupture_strength_limit,
                'Elongation After Fracture (%)': item.irpercentage_elongation,
                'Entry Time': entry_time.strftime('%Y-%m-%d %H:%M:%S') if entry_time else '',
                'Updated At': modify_time.strftime('%Y-%m-%d %H:%M:%S') if modify_time else ''
            })
            
        df = pd.DataFrame(data)
        
        # 创建Excel文件
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Irradiation Creep')
            
        # 设置响应头
        output.seek(0)
        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename=irradiation_creep_{datetime.now().strftime("%Y%m%d%H%M%S")}.xlsx'
        
        return response

class HardeningViewSet(viewsets.ModelViewSet):
    """CRUD, filtering, import and export for the existing hardenings table."""
    queryset = Hardening.objects.select_related(
        'material', 'process', 'irradiat', 'document'
    ).all().order_by('-entry_time')
    serializer_class = HardeningSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'material__material_id',
        'process__process_id',
        'irradiat__irradiat_id',
        'document__document_id',
    ]
    search_fields = ['hardening_id', 'phase_structure', 'material__material_name', 'document__doc_name']
    ordering_fields = ['entry_time', 'modify_time', 'pre_hv', 'post_hv', 'delta_hv']
    pagination_class = StandardResultsSetPagination

    ID_FILTERS = {
        'hardening_id': 'hardening_id',
        'material_id': 'material_id',
        'process_id': 'process_id',
        'irradiat_id': 'irradiat_id',
        'document_id': 'document_id',
    }
    RANGE_FILTERS = {
        'pre_hv': ('pre_hv_min', 'pre_hv_max'),
        'post_hv': ('post_hv_min', 'post_hv_max'),
        'delta_hv': ('delta_hv_min', 'delta_hv_max'),
    }

    @staticmethod
    def _has_value(value):
        return value is not None and value != ''

    @classmethod
    def _apply_filters(cls, queryset, source):
        for param, model_field in cls.ID_FILTERS.items():
            value = source.get(param)
            if not cls._has_value(value):
                continue
            try:
                queryset = queryset.filter(**{model_field: int(value)})
            except (TypeError, ValueError):
                continue

        phase_structure = source.get('phase_structure')
        if cls._has_value(phase_structure):
            queryset = queryset.filter(phase_structure__icontains=str(phase_structure).strip())

        for field, (min_param, max_param) in cls.RANGE_FILTERS.items():
            min_value = source.get(min_param)
            max_value = source.get(max_param)
            if cls._has_value(min_value):
                try:
                    queryset = queryset.filter(**{f'{field}__gte': float(min_value)})
                except (TypeError, ValueError):
                    pass
            if cls._has_value(max_value):
                try:
                    queryset = queryset.filter(**{f'{field}__lte': float(max_value)})
                except (TypeError, ValueError):
                    pass
        return queryset

    def get_queryset(self):
        return self._apply_filters(super().get_queryset(), self.request.query_params)

    @action(detail=False, methods=['post'])
    def batch_delete(self, request):
        ids = request.data.get('ids', [])
        if not isinstance(ids, list) or not ids:
            return Response(
                {'error': 'Please provide a non-empty list of hardening IDs.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            normalized_ids = [int(item) for item in ids]
        except (TypeError, ValueError):
            return Response(
                {'error': 'Every hardening ID must be an integer.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        deleted_count, _ = Hardening.objects.filter(hardening_id__in=normalized_ids).delete()
        return Response({'message': f'Successfully deleted {deleted_count} record(s).'})

    @staticmethod
    def _safe_int(value, field_name, required=True):
        if value is None or pd.isna(value) or str(value).strip() == '':
            if required:
                raise ValueError(f'{field_name} is required')
            return None
        numeric = float(str(value).strip())
        if not numeric.is_integer():
            raise ValueError(f'{field_name} must be an integer')
        return int(numeric)

    @staticmethod
    def _safe_float(value, field_name):
        if value is None or pd.isna(value) or str(value).strip() == '':
            return None
        numeric = float(str(value).strip())
        if not math.isfinite(numeric):
            raise ValueError(f'{field_name} must be a finite number')
        return numeric

    @staticmethod
    def _safe_text(value):
        if value is None or pd.isna(value):
            return None
        value = str(value).strip()
        return value or None

    @action(detail=False, methods=['post'])
    def import_data(self, request):
        file_obj = request.FILES.get('file')
        if file_obj is None:
            return Response({'error': 'Please select a CSV or Excel file.'}, status=status.HTTP_400_BAD_REQUEST)
        if file_obj.size > 10 * 1024 * 1024:
            return Response({'error': 'The import file cannot exceed 10 MB.'}, status=status.HTTP_400_BAD_REQUEST)

        extension = os.path.splitext(file_obj.name)[1].lower()
        if extension not in ('.csv', '.xlsx', '.xls'):
            return Response({'error': 'Only CSV and Excel files are supported.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if extension == '.csv':
                try:
                    dataframe = pd.read_csv(file_obj, encoding='utf-8-sig')
                except UnicodeDecodeError:
                    file_obj.seek(0)
                    dataframe = pd.read_csv(file_obj, encoding='gb18030')
            else:
                dataframe = pd.read_excel(file_obj)
        except Exception as exc:
            return Response({'error': f'Unable to read the import file: {exc}'}, status=status.HTTP_400_BAD_REQUEST)

        aliases = {
            '辐照硬化ID': 'hardening_id',
            'Irradiation Hardening ID': 'hardening_id',
            '材料ID': 'material_id',
            'Material ID': 'material_id',
            '工艺ID': 'process_id',
            'Process ID': 'process_id',
            '辐照ID': 'irradiat_id',
            'Irradiation ID': 'irradiat_id',
            '文献ID': 'document_id',
            '参考文献ID': 'document_id',
            'Document ID': 'document_id',
            'Reference ID': 'document_id',
            '相结构': 'phase_structure',
            'Phase Structure': 'phase_structure',
            '未辐照硬度': 'pre_hv',
            '未辐照硬度(HV)': 'pre_hv',
            '辐照前硬度': 'pre_hv',
            '辐照前硬度(HV)': 'pre_hv',
            'Pre-Irradiation Hardness': 'pre_hv',
            'Pre-Irradiation Hardness (HV)': 'pre_hv',
            '辐照后硬度': 'post_hv',
            '辐照后硬度(HV)': 'post_hv',
            'Post-Irradiation Hardness': 'post_hv',
            'Post-Irradiation Hardness (HV)': 'post_hv',
            '硬度变化': 'delta_hv',
            '硬度变化(HV)': 'delta_hv',
            'Hardness Change': 'delta_hv',
            'Hardness Change (HV)': 'delta_hv',
        }
        dataframe.rename(
            columns=lambda column: aliases.get(str(column).strip(), str(column).strip()),
            inplace=True,
        )

        required_columns = ['material_id', 'process_id', 'irradiat_id', 'document_id']
        missing_columns = [column for column in required_columns if column not in dataframe.columns]
        if missing_columns:
            return Response(
                {
                    'error': f'Missing required columns: {", ".join(missing_columns)}',
                    'required_columns': required_columns,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        created_count = 0
        updated_count = 0
        errors = []
        for index, row in dataframe.iterrows():
            row_number = index + 2
            try:
                hardening_id = self._safe_int(row.get('hardening_id'), 'hardening_id', required=False)
                payload = {
                    'material_id': self._safe_int(row.get('material_id'), 'material_id'),
                    'process_id': self._safe_int(row.get('process_id'), 'process_id'),
                    'irradiat_id': self._safe_int(row.get('irradiat_id'), 'irradiat_id'),
                    'document_id': self._safe_int(row.get('document_id'), 'document_id'),
                    'phase_structure': self._safe_text(row.get('phase_structure')),
                    'pre_hv': self._safe_float(row.get('pre_hv'), 'pre_hv'),
                    'post_hv': self._safe_float(row.get('post_hv'), 'post_hv'),
                    'delta_hv': self._safe_float(row.get('delta_hv'), 'delta_hv'),
                }

                instance = None
                if hardening_id is not None:
                    instance = Hardening.objects.filter(hardening_id=hardening_id).first()
                    if instance is None:
                        raise ValueError(f'hardening_id {hardening_id} does not exist')

                with transaction.atomic():
                    serializer = self.get_serializer(instance, data=payload)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                if instance is None:
                    created_count += 1
                else:
                    updated_count += 1
            except Exception as exc:
                errors.append(f'Row {row_number}: {exc}')

        success_count = created_count + updated_count
        return Response({
            'success': success_count > 0,
            'message': f'Imported {success_count} record(s); {len(errors)} row(s) failed.',
            'success_count': success_count,
            'created_count': created_count,
            'updated_count': updated_count,
            'error_count': len(errors),
            'errors': errors[:20],
        })

    @action(detail=False, methods=['post'])
    def range_query(self, request):
        queryset = Hardening.objects.select_related(
            'material', 'process', 'irradiat', 'document'
        ).all().order_by('-entry_time')
        queryset = self._apply_filters(queryset, request.data)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response(self.get_serializer(queryset, many=True).data)

    @staticmethod
    def _format_datetime(value):
        if value is None:
            return ''
        if timezone.is_aware(value):
            value = timezone.localtime(value)
        return value.strftime('%Y-%m-%d %H:%M:%S')

    @action(detail=False, methods=['post'])
    def export_data(self, request):
        format_type = str(request.data.get('format', 'excel')).lower()
        property_ids = request.data.get('property_ids', [])
        queryset = Hardening.objects.select_related(
            'material', 'process', 'irradiat', 'document'
        ).all().order_by('-entry_time')

        if property_ids:
            try:
                property_ids = [int(item) for item in property_ids]
            except (TypeError, ValueError):
                return Response({'error': 'Invalid hardening ID list.'}, status=status.HTTP_400_BAD_REQUEST)
            queryset = queryset.filter(hardening_id__in=property_ids)

        columns = [
            'Irradiation Hardening ID', 'Material ID', 'Material Name', 'Process ID',
            'Irradiation ID', 'Document ID', 'Document Name', 'Phase Structure',
            'Pre-Irradiation Hardness (HV)', 'Post-Irradiation Hardness (HV)',
            'Hardness Change (HV)', 'Entry Time', 'Updated At',
        ]
        rows = []
        for item in queryset:
            rows.append({
                'Irradiation Hardening ID': item.hardening_id,
                'Material ID': item.material_id,
                'Material Name': item.material.material_name,
                'Process ID': item.process_id,
                'Irradiation ID': item.irradiat_id,
                'Document ID': item.document_id,
                'Document Name': item.document.doc_name,
                'Phase Structure': item.phase_structure,
                'Pre-Irradiation Hardness (HV)': item.pre_hv,
                'Post-Irradiation Hardness (HV)': item.post_hv,
                'Hardness Change (HV)': item.delta_hv,
                'Entry Time': self._format_datetime(item.entry_time),
                'Updated At': self._format_datetime(item.modify_time),
            })
        dataframe = pd.DataFrame(rows, columns=columns)

        if format_type == 'csv':
            response = HttpResponse(content_type='text/csv; charset=utf-8')
            response['Content-Disposition'] = 'attachment; filename="irradiation_hardening.csv"'
            dataframe.to_csv(response, index=False, encoding='utf-8-sig')
        elif format_type in ('excel', 'xlsx'):
            response = HttpResponse(
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename="irradiation_hardening.xlsx"'
            with pd.ExcelWriter(response, engine='openpyxl') as writer:
                dataframe.to_excel(writer, index=False, sheet_name='Irradiation Hardening')
        else:
            return Response({'error': 'format must be excel or csv.'}, status=status.HTTP_400_BAD_REQUEST)

        response['Access-Control-Expose-Headers'] = 'Content-Disposition'
        return response


class DocumentViewSet(viewsets.ModelViewSet):
    """参考文献视图集"""
    queryset = Document.objects.all().order_by('-entry_time')
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['document_id', 'doc_name', 'doc_doi']
    ordering_fields = ['entry_time', 'modify_time']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """自定义查询集"""
        queryset = super().get_queryset()
        
        # 按文献名称搜索
        doc_name = self.request.query_params.get('doc_name')
        if doc_name:
            queryset = queryset.filter(doc_name__icontains=doc_name)
            
        # 按DOI搜索
        doc_doi = self.request.query_params.get('doc_doi')
        if doc_doi:
            queryset = queryset.filter(doc_doi__icontains=doc_doi)
            
        return queryset
    
    def create(self, request, *args, **kwargs):
        """创建参考文献"""
        # 获取请求数据
        data = request.data.copy()
        
        # 记录日志
        logger.info("Document create request received")
        
        # 检查URL格式 - 更宽松的处理
        if 'doc_url' in data and data['doc_url']:
            url = str(data['doc_url']).strip()
            # 如果URL不以http://或https://开头，则添加https://前缀
            if not url.startswith(('http://', 'https://')):
                data['doc_url'] = 'https://' + url
                logger.info(f"URL格式处理后: {data['doc_url']}")
        
        # 使用序列化器验证数据
        serializer = self.get_serializer(data=data)
        if not serializer.is_valid():
            logger.error(f"序列化器验证失败: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            serializer.save()
            logger.info("参考文献创建成功")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"保存数据时出错: {str(e)}")
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def import_data(self, request):
        """导入参考文献数据"""
        try:
            file = request.FILES.get('file')
            if not file:
                return Response({"detail": "没有上传文件"}, status=status.HTTP_400_BAD_REQUEST)
                
            # 检查文件扩展名
            if not file.name.endswith(('.xlsx', '.xls')):
                return Response({"detail": "只支持Excel文件格式"}, status=status.HTTP_400_BAD_REQUEST)
                
            # 读取Excel文件
            df = pd.read_excel(file)
            
            # 记录导入结果
            success_count = 0
            error_count = 0
            errors = []
            
            # 输出列名，帮助调试
            columns = df.columns.tolist()
            logger.info(f"Excel文件列名: {columns}")
            
            # 查找合适的列名
            name_columns = [col for col in columns if '名称' in col or 'name' in col.lower() or '标题' in col]
            doi_columns = [col for col in columns if 'doi' in col.lower()]
            url_columns = [col for col in columns if 'url' in col.lower() or '链接' in col]
            
            # 选择最合适的列名
            name_col = name_columns[0] if name_columns else '文献名称'
            doi_col = doi_columns[0] if doi_columns else '文献DOI号'
            url_col = url_columns[0] if url_columns else '在线链接'
            
            logger.info(f"使用列名: 名称={name_col}, DOI={doi_col}, URL={url_col}")
            
            # 处理每一行数据
            for index, row in df.iterrows():
                try:
                    # 输出行数据，帮助调试
                    logger.debug("Processing document import row %s", index + 2)
                    
                    # 尝试获取数据，先尝试精确匹配，再尝试模糊匹配
                    doc_name = None
                    if name_col in row:
                        doc_name = str(row[name_col]).strip()
                    else:
                        # 尝试遍历所有列找匹配项
                        for col in columns:
                            if ('名称' in col or 'name' in col.lower() or '标题' in col) and pd.notna(row[col]):
                                doc_name = str(row[col]).strip()
                                break
                    
                    doc_doi = None
                    if doi_col in row:
                        doc_doi = str(row[doi_col]).strip()
                    else:
                        for col in columns:
                            if 'doi' in col.lower() and pd.notna(row[col]):
                                doc_doi = str(row[col]).strip()
                                break
                    
                    doc_url = None
                    if url_col in row:
                        doc_url = str(row[url_col]).strip()
                    else:
                        for col in columns:
                            if ('url' in col.lower() or '链接' in col) and pd.notna(row[col]):
                                doc_url = str(row[col]).strip()
                                break
                    
                    # 准备数据
                    data = {
                        'doc_name': doc_name if doc_name is not None else '',
                        'doc_doi': doc_doi if doc_doi is not None else '',
                        'doc_url': doc_url if doc_url is not None else ''
                    }
                    
                    # 记录准备的数据
                    logger.debug("Validated document import row %s", index + 2)
                    
                    # 验证数据
                    if not data['doc_name'] or data['doc_name'] == 'nan':
                        errors.append(f"第{index+2}行: 文献名称不能为空")
                        error_count += 1
                        continue
                        
                    if not data['doc_doi'] or data['doc_doi'] == 'nan':
                        errors.append(f"第{index+2}行: 文献DOI号不能为空")
                        error_count += 1
                        continue
                        
                    if not data['doc_url'] or data['doc_url'] == 'nan':
                        errors.append(f"第{index+2}行: 在线链接不能为空")
                        error_count += 1
                        continue
                    
                    # 验证URL格式
                    if not data['doc_url'].startswith(('http://', 'https://')):
                        data['doc_url'] = 'https://' + data['doc_url']
                    
                    # 创建记录
                    serializer = self.get_serializer(data=data)
                    if serializer.is_valid():
                        serializer.save()
                        success_count += 1
                    else:
                        error_message = "; ".join([f"{key}: {value[0]}" for key, value in serializer.errors.items()])
                        errors.append(f"第{index+2}行: {error_message}")
                        error_count += 1
                except Exception as e:
                    logger.error(f"导入第{index+2}行时出错: {str(e)}")
                    errors.append(f"第{index+2}行: {str(e)}")
                    error_count += 1
            
            # 返回导入结果
            return Response({
                "detail": "导入完成",
                "success_count": success_count,
                "error_count": error_count,
                "errors": errors
            })
        except Exception as e:
            logger.error(f"导入参考文献失败: {str(e)}")
            return Response({"detail": f"导入失败: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def export_data(self, request):
        """导出参考文献数据"""
        try:
            from django.utils import timezone
            
            property_ids = request.data.get('property_ids', [])
            format_type = request.data.get('format', 'excel')
            logger.info(
                "Document export requested: format=%s, selected_records=%s",
                format_type,
                len(property_ids),
            )
            
            if format_type != 'excel':
                return Response({
                    'error': '目前只支持Excel格式导出'
                }, status=status.HTTP_400_BAD_REQUEST)
                
            # 获取要导出的数据
            if property_ids:
                logger.debug("Exporting selected document records")
                queryset = Document.objects.filter(document_id__in=property_ids)
            else:
                logger.info("导出全部参考文献")
                queryset = self.get_queryset()
                
            # 记录数据量
            count = queryset.count()
            logger.info(f"查询到 {count} 条参考文献记录")
            
            # 创建DataFrame
            data = []
            for item in queryset:
                try:
                    # 转换时间为本地时区
                    entry_time = timezone.localtime(item.entry_time) if item.entry_time and hasattr(item.entry_time, 'tzinfo') else None
                    modify_time = timezone.localtime(item.modify_time) if item.modify_time and hasattr(item.modify_time, 'tzinfo') else None
                    
                    data.append({
                        'Document ID': item.document_id,
                        'Document Name': item.doc_name,
                        'DOI': item.doc_doi,
                        'URL': item.doc_url,
                        'Entry Time': entry_time.strftime('%Y-%m-%d %H:%M:%S') if entry_time else '',
                        'Updated At': modify_time.strftime('%Y-%m-%d %H:%M:%S') if modify_time else ''
                    })
                except Exception as e:
                    logger.error(f"处理参考文献ID {item.document_id} 时出错: {str(e)}")
                    continue
                
            # 如果没有数据
            if not data:
                logger.warning("没有找到可导出的数据")
                return Response({"detail": "没有数据可导出"}, status=status.HTTP_404_NOT_FOUND)
            
            logger.info(f"准备导出 {len(data)} 条参考文献记录")
            df = pd.DataFrame(data)
            
            try:
                # 创建Excel文件
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='References')
                    
                # 设置响应头
                output.seek(0)
                file_content = output.read()
                logger.info(f"Excel文件生成成功, 大小: {len(file_content)} 字节")
                
                # 设置文件名
                filename = f"references_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
                
                # 设置响应
                response = HttpResponse(
                    file_content,
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                response['Access-Control-Expose-Headers'] = 'Content-Disposition'
                
                logger.info(f"参考文献数据导出成功: {filename}")
                return response
            except Exception as e:
                logger.error(f"生成Excel文件时出错: {str(e)}")
                raise
        except Exception as e:
            logger.error(f"导出参考文献数据失败: {str(e)}", exc_info=True)
            return Response({"detail": f"导出失败: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
