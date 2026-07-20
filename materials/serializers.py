from rest_framework import serializers
from .models import (
    Material, Process, RoomTempProperty, MaterialProperty, 
    HTProperty, ImpTest, CreTest, FatTest, IrrCondition, MicrostructureEvolution, Embrittlement, IrrCreep, Document,
    Hardening
)
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class ProcessSerializer(serializers.ModelSerializer):
    """工艺序列化器"""
    class Meta:
        model = Process
        fields = '__all__'
        read_only_fields = ['process_id', 'entry_time', 'modify_time']

    def validate(self, data):
        # 验证制备工艺
        if not data.get('fabrication'):
            raise serializers.ValidationError("制备工艺不能为空")

        # 热处理字段映射
        heat_treatment_fields = {
            'homogenization': ['homogenize_temp', 'homogenize_time'],
            'normalization': ['normalize_temp', 'normalize_time'],
            'annealing': ['annealing_temp', 'annealing_time'],
            'tempering': ['tempering_temp', 'tempering_time'],
            'quenching': ['quenching_temp', 'quenching_type'],
            'rolling': ['rolling_temp', 'reduction']
        }

        # 检查热处理字段
        for treatment, fields in heat_treatment_fields.items():
            treatment_enabled = data.get(treatment, False)
            
            # 如果热处理开启
            if treatment_enabled:
                for field in fields:
                    # 如果字段不存在或为空，设置为默认值
                    if field not in data or data[field] is None or (isinstance(data[field], str) and not data[field].strip()):
                        if field.endswith('_temp'):
                            data[field] = 0
                        elif field.endswith('_time'):
                            data[field] = 0
                        elif field == 'quenching_type':
                            data[field] = ''
                        elif field == 'reduction':
                            data[field] = 0
            else:
                # 如果热处理关闭，将相关字段设为None
                for field in fields:
                    data[field] = None

        # 验证温度字段
        temp_fields = {
            'homogenize_temp': '均匀化温度',
            'normalize_temp': '正火温度',
            'annealing_temp': '退火温度',
            'tempering_temp': '回火温度',
            'quenching_temp': '淬火温度',
            'rolling_temp': '轧制温度'
        }
        for field, name in temp_fields.items():
            if field in data and data[field] is not None:
                try:
                    temp_value = float(data[field])
                    if temp_value < 0:
                        data[field] = 0
                    else:
                        data[field] = temp_value
                except (ValueError, TypeError):
                    data[field] = 0

        # 验证时间字段
        time_fields = {
            'homogenize_time': '均匀化时间',
            'normalize_time': '正火时间',
            'annealing_time': '退火时间',
            'tempering_time': '回火时间'
        }
        for field, name in time_fields.items():
            if field in data and data[field] is not None:
                try:
                    time_value = float(data[field])
                    if time_value < 0:
                        data[field] = 0
                    else:
                        data[field] = time_value
                except (ValueError, TypeError):
                    data[field] = 0

        # 验证压下量
        if 'reduction' in data and data['reduction'] is not None:
            try:
                reduction_value = float(data['reduction'])
                if reduction_value < 0:
                    data['reduction'] = 0
                elif reduction_value > 100:
                    data['reduction'] = 100
                else:
                    data['reduction'] = reduction_value
            except (ValueError, TypeError):
                data['reduction'] = 0

        return data

    def to_representation(self, instance):
        """自定义数据表示"""
        data = super().to_representation(instance)
        
        # 确保所有数值字段都是浮点数
        float_fields = [
            'homogenize_temp', 'homogenize_time',
            'normalize_temp', 'normalize_time',
            'annealing_temp', 'annealing_time',
            'tempering_temp', 'tempering_time',
            'quenching_temp', 'rolling_temp',
            'reduction'
        ]
        
        for field in float_fields:
            if field in data and data[field] is not None:
                try:
                    data[field] = float(data[field])
                except (ValueError, TypeError):
                    data[field] = None
        
        return data

class MaterialSerializer(serializers.ModelSerializer):
    total_composition = serializers.SerializerMethodField()

    class Meta:
        model = Material
        fields = '__all__'
        read_only_fields = ('material_id', 'entry_time', 'modify_time')

    def validate_material_name(self, value):
        """验证材料名称是否已存在"""
        if self.instance is None:  # 创建新记录时
            if Material.objects.filter(material_name=value).exists():
                raise serializers.ValidationError("该材料名称已存在")
        else:  # 更新记录时
            if Material.objects.filter(material_name=value).exclude(material_id=self.instance.material_id).exists():
                raise serializers.ValidationError("该材料名称已存在")
        return value

    def get_total_composition(self, obj):
        """计算元素总含量"""
        composition_fields = [
            'composition_al', 'composition_c', 'composition_co', 'composition_cr',
            'composition_cu', 'composition_fe', 'composition_hf', 'composition_mg',
            'composition_mn', 'composition_mo', 'composition_n', 'composition_nb',
            'composition_ni', 'composition_sc', 'composition_si', 'composition_sn',
            'composition_ta', 'composition_ti', 'composition_v', 'composition_w',
            'composition_y', 'composition_zn', 'composition_zr'
        ]
        return sum(getattr(obj, field, 0) for field in composition_fields)

    def validate(self, data):
        """验证元素含量总和不超过100%"""
        composition_fields = [
            'composition_al', 'composition_c', 'composition_co', 'composition_cr',
            'composition_cu', 'composition_fe', 'composition_hf', 'composition_mg',
            'composition_mn', 'composition_mo', 'composition_n', 'composition_nb',
            'composition_ni', 'composition_sc', 'composition_si', 'composition_sn',
            'composition_ta', 'composition_ti', 'composition_v', 'composition_w',
            'composition_y', 'composition_zn', 'composition_zr'
        ]
        
        total_composition = sum(data.get(field, 0) for field in composition_fields)
        # 允许由浮点精度导致的轻微超出：例如每个元素为两位小数但求和可能得到 100.0000001
        if round(total_composition, 2) > 100:
            raise serializers.ValidationError("所有元素含量总和不能超过100%")
        return data

class RoomTempPropertySerializer(serializers.ModelSerializer):
    material_id = serializers.IntegerField(write_only=True)
    process_id = serializers.IntegerField(write_only=True)
    material = serializers.SerializerMethodField()
    process = serializers.SerializerMethodField()

    class Meta:
        model = RoomTempProperty
        fields = [
            'rtproperty_id',
            'material_id',
            'process_id',
            'material',
            'process',
            'phase_structure',
            'hardness_value',
            'yield_strength_c',
            'yield_strength_t',
            'ultimate_strength_c',
            'ultimate_strength_t',
            'fracture_strain_c',
            'fracture_strain_t',
            'entry_time',
            'modify_time'
        ]
        read_only_fields = ['rtproperty_id', 'entry_time', 'modify_time']

    def get_material(self, obj):
        return {
            'material_id': obj.material.material_id,
            'material_name': obj.material.material_name if hasattr(obj.material, 'material_name') else None
        }

    def get_process(self, obj):
        return {
            'process_id': obj.process.process_id,
            'fabrication': obj.process.fabrication if hasattr(obj.process, 'fabrication') else None
        }

    def create(self, validated_data):
        material_id = validated_data.pop('material_id')
        process_id = validated_data.pop('process_id')
        
        try:
            material = Material.objects.get(material_id=material_id)
            process = Process.objects.get(process_id=process_id)
            
            return RoomTempProperty.objects.create(
                material=material,
                process=process,
                **validated_data
            )
        except Material.DoesNotExist:
            raise serializers.ValidationError({'material_id': '材料不存在'})
        except Process.DoesNotExist:
            raise serializers.ValidationError({'process_id': '工艺不存在'})

    def update(self, instance, validated_data):
        material_id = validated_data.pop('material_id', None)
        process_id = validated_data.pop('process_id', None)
        
        if material_id is not None:
            try:
                material = Material.objects.get(material_id=material_id)
                instance.material = material
            except Material.DoesNotExist:
                raise serializers.ValidationError({'material_id': '材料不存在'})
        
        if process_id is not None:
            try:
                process = Process.objects.get(process_id=process_id)
                instance.process = process
            except Process.DoesNotExist:
                raise serializers.ValidationError({'process_id': '工艺不存在'})
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance

class MaterialSearchSerializer(serializers.Serializer):
    """材料搜索序列化器"""
    keyword = serializers.CharField(required=False, help_text='搜索关键词')
    elements = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text='元素列表'
    )
    page = serializers.IntegerField(required=False, default=1, help_text='页码')
    page_size = serializers.IntegerField(required=False, default=10, help_text='每页数量')

class MaterialRangeQuerySerializer(serializers.Serializer):
    """材料范围查询序列化器"""
    element = serializers.CharField(help_text='元素名称')
    min_value = serializers.FloatField(help_text='最小值')
    max_value = serializers.FloatField(help_text='最大值')

class MaterialMultiConditionSerializer(serializers.Serializer):
    """材料多条件查询序列化器"""
    conditions = serializers.ListField(
        child=MaterialRangeQuerySerializer(),
        help_text='查询条件列表'
    )
    page = serializers.IntegerField(required=False, default=1, help_text='页码')
    page_size = serializers.IntegerField(required=False, default=10, help_text='每页数量')

class MaterialExportSerializer(serializers.Serializer):
    """材料导出序列化器"""
    format = serializers.ChoiceField(choices=['excel'], default='excel')
    search_results = serializers.ListField(
        child=MaterialSerializer(),
        help_text='要导出的材料数据列表'
    )

class MaterialImportSerializer(serializers.Serializer):
    """材料导入序列化器"""
    file = serializers.FileField(help_text='Excel文件')

    def validate_file(self, value):
        """验证上传的文件"""
        # 检查文件类型
        if not value.name.endswith(('.xlsx', '.xls')):
            raise serializers.ValidationError('只支持 Excel 文件格式 (.xlsx, .xls)')

        # 检查文件大小（限制为10MB）
        if value.size > 10 * 1024 * 1024:  # 10MB in bytes
            raise serializers.ValidationError('文件大小不能超过10MB')
        
        try:
            # 尝试读取Excel文件
            df = pd.read_excel(value)
            
            # 验证必需列
            required_columns = ['material_name']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise serializers.ValidationError(f'Excel文件缺少必需列: {", ".join(missing_columns)}')

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
                raise serializers.ValidationError('Excel文件必须包含至少一个元素成分列')

            # 验证数据格式
            material_names = set()
            for index, row in df.iterrows():
                # 验证材料名称
                material_name = str(row['material_name']).strip()
                if pd.isna(material_name) or material_name == '':
                    raise serializers.ValidationError(f'第{index + 2}行: 材料名称不能为空')
                
                # 检查材料名称是否重复
                if material_name in material_names:
                    raise serializers.ValidationError(f'第{index + 2}行: 材料名称 "{material_name}" 在文件中重复')
                material_names.add(material_name)

                # 验证元素含量
                total_composition = 0
                for col in available_element_columns:
                    try:
                        value = float(row[col]) if pd.notna(row[col]) else 0
                        if value < 0:
                            raise serializers.ValidationError(f'第{index + 2}行: 元素含量不能为负数: {col}')
                        total_composition += value
                    except (ValueError, TypeError):
                        raise serializers.ValidationError(f'第{index + 2}行: 元素含量必须为数字: {col}')

                if round(total_composition, 2) > 100:
                    raise serializers.ValidationError(f'第{index + 2}行: 元素含量总和不能超过100%')

        except pd.errors.EmptyDataError:
            raise serializers.ValidationError('Excel文件为空')
        except Exception as e:
            raise serializers.ValidationError(f'Excel文件格式错误: {str(e)}')

        return value

class MaterialBatchDeleteSerializer(serializers.Serializer):
    """批量删除序列化器"""
    material_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text='材料ID列表'
    )

class HTPropertySerializer(serializers.ModelSerializer):
    material_id = serializers.IntegerField(write_only=True)
    process_id = serializers.IntegerField(write_only=True)
    material = serializers.SerializerMethodField()
    process = serializers.SerializerMethodField()
    
    class Meta:
        model = HTProperty
        fields = [
            'htproperty_id',
            'material_id',
            'process_id',
            'material',
            'process',
            'test_type',
            'htproperty_temp',
            'yield_strength',
            'ultimate_strength',
            'fracture_strain',
            'entry_time',
            'modify_time'
        ]
        read_only_fields = ['htproperty_id', 'entry_time', 'modify_time']

    def get_material(self, obj):
        return {
            'material_id': obj.material.material_id,
            'material_name': obj.material.material_name if hasattr(obj.material, 'material_name') else None
        }

    def get_process(self, obj):
        return {
            'process_id': obj.process.process_id,
            'fabrication': obj.process.fabrication if hasattr(obj.process, 'fabrication') else None
        }

    def create(self, validated_data):
        material_id = validated_data.pop('material_id')
        process_id = validated_data.pop('process_id')
        
        try:
            material = Material.objects.get(material_id=material_id)
            process = Process.objects.get(process_id=process_id)
            
            return HTProperty.objects.create(
                material=material,
                process=process,
                **validated_data
            )
        except Material.DoesNotExist:
            raise serializers.ValidationError({'material_id': '材料不存在'})
        except Process.DoesNotExist:
            raise serializers.ValidationError({'process_id': '工艺不存在'})

    def update(self, instance, validated_data):
        material_id = validated_data.pop('material_id', None)
        process_id = validated_data.pop('process_id', None)
        
        if material_id is not None:
            try:
                material = Material.objects.get(material_id=material_id)
                instance.material = material
            except Material.DoesNotExist:
                raise serializers.ValidationError({'material_id': '材料不存在'})
        
        if process_id is not None:
            try:
                process = Process.objects.get(process_id=process_id)
                instance.process = process
            except Process.DoesNotExist:
                raise serializers.ValidationError({'process_id': '工艺不存在'})
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance

    def validate(self, data):
        """自定义验证"""
        # 验证测试温度
        htproperty_temp = data.get('htproperty_temp')
        if htproperty_temp is not None and htproperty_temp < 0:
            raise serializers.ValidationError({"htproperty_temp": "测试温度不能为负值"})

        # 验证测试类型
        test_type = data.get('test_type')
        if not test_type:
            raise serializers.ValidationError({"test_type": "测试类型不能为空"})

        return data

class ImpTestSerializer(serializers.ModelSerializer):
    material_id = serializers.IntegerField(write_only=True)
    process_id = serializers.IntegerField(write_only=True)
    material = serializers.SerializerMethodField()
    process = serializers.SerializerMethodField()
    
    class Meta:
        model = ImpTest
        fields = [
            'impact_id',
            'material_id',
            'process_id',
            'material',
            'process',
            'impact_temp',
            'impact_type',
            'impact_energy',
            'absorbed_energy',
            'impact_tough_value',
            'fracture_type',
            'entry_time',
            'modify_time'
        ]
        read_only_fields = ['impact_id', 'entry_time', 'modify_time']

    def get_material(self, obj):
        return {
            'material_id': obj.material.material_id,
            'material_name': obj.material.material_name if hasattr(obj.material, 'material_name') else None
        }

    def get_process(self, obj):
        return {
            'process_id': obj.process.process_id,
            'fabrication': obj.process.fabrication if hasattr(obj.process, 'fabrication') else None
        }

    def create(self, validated_data):
        material_id = validated_data.pop('material_id')
        process_id = validated_data.pop('process_id')
        
        try:
            material = Material.objects.get(material_id=material_id)
            process = Process.objects.get(process_id=process_id)
            
            return ImpTest.objects.create(
                material=material,
                process=process,
                **validated_data
            )
        except Material.DoesNotExist:
            raise serializers.ValidationError({'material_id': '材料不存在'})
        except Process.DoesNotExist:
            raise serializers.ValidationError({'process_id': '工艺不存在'})

    def update(self, instance, validated_data):
        material_id = validated_data.pop('material_id', None)
        process_id = validated_data.pop('process_id', None)
        
        if material_id is not None:
            try:
                material = Material.objects.get(material_id=material_id)
                instance.material = material
            except Material.DoesNotExist:
                raise serializers.ValidationError({'material_id': '材料不存在'})
        
        if process_id is not None:
            try:
                process = Process.objects.get(process_id=process_id)
                instance.process = process
            except Process.DoesNotExist:
                raise serializers.ValidationError({'process_id': '工艺不存在'})
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance

    def validate(self, data):
        """自定义验证"""
        # 验证测试温度
        impact_temp = data.get('impact_temp')
        if impact_temp is not None and impact_temp < -273.15:  # 绝对零度
            raise serializers.ValidationError({"impact_temp": "测试温度不能低于绝对零度"})

        return data

class CreTestSerializer(serializers.ModelSerializer):
    """蠕变测试序列化器"""
    # 嵌套序列化Material和Process
    material = serializers.PrimaryKeyRelatedField(queryset=Material.objects.all(), required=False)
    process = serializers.PrimaryKeyRelatedField(queryset=Process.objects.all(), required=False)
    
    class Meta:
        model = CreTest
        fields = '__all__'
        read_only_fields = ['creep_id', 'entry_time', 'modify_time']
    
    def to_representation(self, instance):
        """
        重写数据表示方法，添加关联的material和process信息
        """
        representation = super().to_representation(instance)
        representation['material'] = {
            'material_id': instance.material.material_id,
            'material_name': instance.material.material_name
        }
        representation['process'] = {
            'process_id': instance.process.process_id,
            'fabrication': instance.process.fabrication
        }
        return representation
    
    def validate(self, data):
        """数据验证"""
        # 验证material_id
        material_id = self.initial_data.get('material_id')
        if material_id:
            try:
                material = Material.objects.get(material_id=material_id)
                data['material'] = material
            except Material.DoesNotExist:
                raise serializers.ValidationError(f"材料ID {material_id} 不存在")
        
        # 验证process_id
        process_id = self.initial_data.get('process_id')
        if process_id:
            try:
                process = Process.objects.get(process_id=process_id)
                data['process'] = process
            except Process.DoesNotExist:
                raise serializers.ValidationError(f"工艺ID {process_id} 不存在")
        
        return data

class FatTestSerializer(serializers.ModelSerializer):
    """疲劳测试序列化器"""
    material_id = serializers.IntegerField(write_only=True)
    process_id = serializers.IntegerField(write_only=True)
    material = serializers.SerializerMethodField()
    process = serializers.SerializerMethodField()
    
    class Meta:
        model = FatTest
        fields = [
            'fatigue_id',
            'material_id',
            'process_id',
            'material',
            'process',
            'fatigue_method',
            'stress_ratio',
            'stress_range',
            'mean_stress',
            'loading_frequency',
            'environment_temp',
            'fatigue_life',
            'fatigue_limit',
            'entry_time',
            'modify_time'
        ]
        read_only_fields = ['fatigue_id', 'entry_time', 'modify_time']

    def get_material(self, obj):
        return {
            'material_id': obj.material.material_id,
            'material_name': obj.material.material_name if hasattr(obj.material, 'material_name') else None
        }

    def get_process(self, obj):
        return {
            'process_id': obj.process.process_id,
            'fabrication': obj.process.fabrication if hasattr(obj.process, 'fabrication') else None
        }

    def create(self, validated_data):
        material_id = validated_data.pop('material_id')
        process_id = validated_data.pop('process_id')
        
        try:
            material = Material.objects.get(material_id=material_id)
            process = Process.objects.get(process_id=process_id)
            
            return FatTest.objects.create(
                material=material,
                process=process,
                **validated_data
            )
        except Material.DoesNotExist:
            raise serializers.ValidationError({'material_id': '材料不存在'})
        except Process.DoesNotExist:
            raise serializers.ValidationError({'process_id': '工艺不存在'})
        except Exception as e:
            # 记录其他可能的异常
            logger.error(f"创建疲劳测试记录时发生错误: {str(e)}")
            raise serializers.ValidationError({'detail': f'创建记录失败: {str(e)}'})

    def update(self, instance, validated_data):
        material_id = validated_data.pop('material_id', None)
        process_id = validated_data.pop('process_id', None)
        
        try:
            # 记录接收到的数据
            logger.info(
                "Updating fatigue test ID=%s; fields=%s",
                instance.fatigue_id,
                sorted(validated_data.keys()),
            )
            
            if material_id is not None:
                try:
                    material = Material.objects.get(material_id=material_id)
                    instance.material = material
                except Material.DoesNotExist:
                    raise serializers.ValidationError({'material_id': '材料不存在'})
            
            if process_id is not None:
                try:
                    process = Process.objects.get(process_id=process_id)
                    instance.process = process
                except Process.DoesNotExist:
                    raise serializers.ValidationError({'process_id': '工艺不存在'})
            
            # 更新其他字段
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            
            instance.save()
            return instance
        except serializers.ValidationError:
            raise  # 重新抛出验证错误
        except Exception as e:
            # 记录异常
            logger.error(f"更新疲劳测试记录ID: {instance.fatigue_id} 时发生错误: {str(e)}")
            raise serializers.ValidationError({'detail': f'更新记录失败: {str(e)}'})

    def validate(self, data):
        """自定义验证"""
        # 验证环境温度
        environment_temp = data.get('environment_temp')
        if environment_temp is not None:
            try:
                environment_temp = float(environment_temp)
                if environment_temp < -273.15:  # 绝对零度
                    raise serializers.ValidationError({"environment_temp": "环境温度不能低于绝对零度"})
            except (ValueError, TypeError):
                raise serializers.ValidationError({"environment_temp": "环境温度必须是有效的数字"})
            
        # 验证疲劳寿命
        fatigue_life = data.get('fatigue_life')
        if fatigue_life is not None:
            try:
                fatigue_life = float(fatigue_life)
                if fatigue_life < 0:
                    raise serializers.ValidationError({"fatigue_life": "疲劳寿命不能为负数"})
            except (ValueError, TypeError):
                raise serializers.ValidationError({"fatigue_life": "疲劳寿命必须是有效的数字"})
            
        # 验证应力比
        stress_ratio = data.get('stress_ratio')
        if stress_ratio is not None and not isinstance(stress_ratio, (int, float)):
            try:
                float(stress_ratio)
            except (ValueError, TypeError):
                raise serializers.ValidationError({"stress_ratio": "应力比必须为数字"})
            
        # 验证应力幅
        stress_range = data.get('stress_range')
        if stress_range is not None and not isinstance(stress_range, (int, float)):
            try:
                float(stress_range)
            except (ValueError, TypeError):
                raise serializers.ValidationError({"stress_range": "应力幅必须为数字"})
            
        # 验证平均应力
        mean_stress = data.get('mean_stress')
        if mean_stress is not None and not isinstance(mean_stress, (int, float)):
            try:
                float(mean_stress)
            except (ValueError, TypeError):
                raise serializers.ValidationError({"mean_stress": "平均应力必须为数字"})
            
        # 验证加载频率
        loading_frequency = data.get('loading_frequency') 
        if loading_frequency is not None and not isinstance(loading_frequency, (int, float)):
            try:
                float(loading_frequency)
            except (ValueError, TypeError):
                raise serializers.ValidationError({"loading_frequency": "加载频率必须为数字"})
            
        # 验证疲劳极限
        fatigue_limit = data.get('fatigue_limit')
        if fatigue_limit is not None and not isinstance(fatigue_limit, (int, float)):
            try:
                float(fatigue_limit)
            except (ValueError, TypeError):
                raise serializers.ValidationError({"fatigue_limit": "疲劳极限必须为数字"})

        return data 

class IrrConditionSerializer(serializers.ModelSerializer):
    """辐照条件序列化器"""
    class Meta:
        model = IrrCondition
        fields = [
            'irradiat_id',
            'irradiat_type',
            'irradiat_energy',
            'irradiat_temp',
            'irradiat_dose',
            'irradiat_fluence',
            'displac_damage',
            'entry_time',
            'modify_time'
        ]
        read_only_fields = ['irradiat_id', 'entry_time', 'modify_time'] 

class MicrostructureEvolutionSerializer(serializers.ModelSerializer):
    """微结构演化序列化器"""
    material_id = serializers.IntegerField(write_only=True)
    process_id = serializers.IntegerField(write_only=True)
    irradiat_id = serializers.IntegerField(write_only=True)
    material = serializers.SerializerMethodField()
    process = serializers.SerializerMethodField()
    irradiat = serializers.SerializerMethodField()
    
    class Meta:
        model = MicrostructureEvolution
        fields = [
            'microstructure_id',
            'material_id',
            'process_id',
            'irradiat_id',
            'material',
            'process',
            'irradiat',
            'he_bubble_diam',
            'he_bubble_dens',
            'swelling_rate',
            'irradiat_hard',
            'entry_time',
            'modify_time'
        ]
        read_only_fields = ['microstructure_id', 'entry_time', 'modify_time']

    def get_material(self, obj):
        return {
            'material_id': obj.material.material_id,
            'material_name': obj.material.material_name if hasattr(obj.material, 'material_name') else None
        }

    def get_process(self, obj):
        return {
            'process_id': obj.process.process_id,
            'fabrication': obj.process.fabrication if hasattr(obj.process, 'fabrication') else None
        }
        
    def get_irradiat(self, obj):
        return {
            'irradiat_id': obj.irradiat.irradiat_id,
            'irradiat_type': obj.irradiat.irradiat_type if hasattr(obj.irradiat, 'irradiat_type') else None
        }

    def create(self, validated_data):
        material_id = validated_data.pop('material_id')
        process_id = validated_data.pop('process_id')
        irradiat_id = validated_data.pop('irradiat_id')
        
        try:
            material = Material.objects.get(material_id=material_id)
            process = Process.objects.get(process_id=process_id)
            irradiat = IrrCondition.objects.get(irradiat_id=irradiat_id)
            
            return MicrostructureEvolution.objects.create(
                material=material,
                process=process,
                irradiat=irradiat,
                **validated_data
            )
        except Material.DoesNotExist:
            raise serializers.ValidationError({'material_id': '材料不存在'})
        except Process.DoesNotExist:
            raise serializers.ValidationError({'process_id': '工艺不存在'})
        except IrrCondition.DoesNotExist:
            raise serializers.ValidationError({'irradiat_id': '辐照条件不存在'})

    def update(self, instance, validated_data):
        if 'material_id' in validated_data:
            material_id = validated_data.pop('material_id')
            try:
                material = Material.objects.get(material_id=material_id)
                instance.material = material
            except Material.DoesNotExist:
                raise serializers.ValidationError({'material_id': '材料不存在'})

        if 'process_id' in validated_data:
            process_id = validated_data.pop('process_id')
            try:
                process = Process.objects.get(process_id=process_id)
                instance.process = process
            except Process.DoesNotExist:
                raise serializers.ValidationError({'process_id': '工艺不存在'})

        if 'irradiat_id' in validated_data:
            irradiat_id = validated_data.pop('irradiat_id')
            try:
                irradiat = IrrCondition.objects.get(irradiat_id=irradiat_id)
                instance.irradiat = irradiat
            except IrrCondition.DoesNotExist:
                raise serializers.ValidationError({'irradiat_id': '辐照条件不存在'})

        return super().update(instance, validated_data) 

class EmbrittlementSerializer(serializers.ModelSerializer):
    """辐照脆化序列化器"""
    material_id = serializers.IntegerField(write_only=True)
    process_id = serializers.IntegerField(write_only=True)
    irradiat_id = serializers.IntegerField(write_only=True)
    material = serializers.SerializerMethodField()
    process = serializers.SerializerMethodField()
    irradiat = serializers.SerializerMethodField()
    
    class Meta:
        model = Embrittlement
        fields = [
            'embrittlement_id',
            'material_id',
            'process_id',
            'irradiat_id',
            'material',
            'process',
            'irradiat',
            'dbtt',
            'dbtt_difference',
            'entry_time',
            'modify_time'
        ]
        read_only_fields = ['embrittlement_id', 'entry_time', 'modify_time']

    def get_material(self, obj):
        return {
            'material_id': obj.material.material_id,
            'material_name': obj.material.material_name if hasattr(obj.material, 'material_name') else None
        }

    def get_process(self, obj):
        return {
            'process_id': obj.process.process_id,
            'fabrication': obj.process.fabrication if hasattr(obj.process, 'fabrication') else None
        }
        
    def get_irradiat(self, obj):
        return {
            'irradiat_id': obj.irradiat.irradiat_id,
            'irradiat_type': obj.irradiat.irradiat_type if hasattr(obj.irradiat, 'irradiat_type') else None
        }

    def create(self, validated_data):
        material_id = validated_data.pop('material_id')
        process_id = validated_data.pop('process_id')
        irradiat_id = validated_data.pop('irradiat_id')
        
        try:
            material = Material.objects.get(material_id=material_id)
            process = Process.objects.get(process_id=process_id)
            irradiat = IrrCondition.objects.get(irradiat_id=irradiat_id)
            
            return Embrittlement.objects.create(
                material=material,
                process=process,
                irradiat=irradiat,
                **validated_data
            )
        except Material.DoesNotExist:
            raise serializers.ValidationError({'material_id': '材料不存在'})
        except Process.DoesNotExist:
            raise serializers.ValidationError({'process_id': '工艺不存在'})
        except IrrCondition.DoesNotExist:
            raise serializers.ValidationError({'irradiat_id': '辐照条件不存在'})

    def update(self, instance, validated_data):
        if 'material_id' in validated_data:
            material_id = validated_data.pop('material_id')
            try:
                material = Material.objects.get(material_id=material_id)
                instance.material = material
            except Material.DoesNotExist:
                raise serializers.ValidationError({'material_id': '材料不存在'})

        if 'process_id' in validated_data:
            process_id = validated_data.pop('process_id')
            try:
                process = Process.objects.get(process_id=process_id)
                instance.process = process
            except Process.DoesNotExist:
                raise serializers.ValidationError({'process_id': '工艺不存在'})

        if 'irradiat_id' in validated_data:
            irradiat_id = validated_data.pop('irradiat_id')
            try:
                irradiat = IrrCondition.objects.get(irradiat_id=irradiat_id)
                instance.irradiat = irradiat
            except IrrCondition.DoesNotExist:
                raise serializers.ValidationError({'irradiat_id': '辐照条件不存在'})

        return super().update(instance, validated_data)

    def validate(self, data):
        """自定义验证"""
        # 验证韧脆转变温度
        dbtt = data.get('dbtt')
        if dbtt is not None and not isinstance(dbtt, (int, float)):
            try:
                float(dbtt)
            except (ValueError, TypeError):
                raise serializers.ValidationError({"dbtt": "韧脆转变温度必须为数字"})
        
        # 验证韧脆转变温度变化
        dbtt_difference = data.get('dbtt_difference')
        if dbtt_difference is not None and not isinstance(dbtt_difference, (int, float)):
            try:
                float(dbtt_difference)
            except (ValueError, TypeError):
                raise serializers.ValidationError({"dbtt_difference": "韧脆转变温度变化必须为数字"})
        
        return data 

class IrrCreepSerializer(serializers.ModelSerializer):
    """辐照蠕变序列化器"""
    material_id = serializers.IntegerField(write_only=True)
    process_id = serializers.IntegerField(write_only=True)
    irradiat_id = serializers.IntegerField(write_only=True)
    material = serializers.SerializerMethodField()
    process = serializers.SerializerMethodField()
    irradiat = serializers.SerializerMethodField()

    class Meta:
        model = IrrCreep
        fields = [
            'ircreep_id',
            'material_id',
            'process_id',
            'irradiat_id',
            'material',
            'process',
            'irradiat',
            'ircreep_temp',
            'ircreep_time',
            'irinitial_stress',
            'ircreep_rate',
            'ircreep_limit',
            'ircreep_rupture_strength',
            'irrupture_time',
            'irrupture_strength_limit',
            'irpercentage_elongation',
            'entry_time',
            'modify_time'
        ]
        read_only_fields = ['ircreep_id', 'entry_time', 'modify_time']

    def get_material(self, obj):
        return {
            'material_id': obj.material.material_id,
            'material_name': obj.material.material_name if hasattr(obj.material, 'material_name') else None
        }

    def get_process(self, obj):
        return {
            'process_id': obj.process.process_id,
            'fabrication': obj.process.fabrication if hasattr(obj.process, 'fabrication') else None
        }

    def get_irradiat(self, obj):
        return {
            'irradiat_id': obj.irradiat.irradiat_id,
            'irradiat_type': obj.irradiat.irradiat_type if hasattr(obj.irradiat, 'irradiat_type') else None
        }

    def create(self, validated_data):
        material_id = validated_data.pop('material_id')
        process_id = validated_data.pop('process_id')
        irradiat_id = validated_data.pop('irradiat_id')
        
        try:
            material = Material.objects.get(material_id=material_id)
            process = Process.objects.get(process_id=process_id)
            irradiat = IrrCondition.objects.get(irradiat_id=irradiat_id)
            
            return IrrCreep.objects.create(
                material=material,
                process=process,
                irradiat=irradiat,
                **validated_data
            )
        except Material.DoesNotExist:
            raise serializers.ValidationError({'material_id': '材料不存在'})
        except Process.DoesNotExist:
            raise serializers.ValidationError({'process_id': '工艺不存在'})
        except IrrCondition.DoesNotExist:
            raise serializers.ValidationError({'irradiat_id': '辐照条件不存在'})
        except Exception as e:
            logger.error(f"创建辐照蠕变记录时发生错误: {str(e)}")
            raise serializers.ValidationError({'detail': f'创建记录失败: {str(e)}'})

    def update(self, instance, validated_data):
        if 'material_id' in validated_data:
            material_id = validated_data.pop('material_id')
            try:
                material = Material.objects.get(material_id=material_id)
                instance.material = material
            except Material.DoesNotExist:
                raise serializers.ValidationError({'material_id': '材料不存在'})

        if 'process_id' in validated_data:
            process_id = validated_data.pop('process_id')
            try:
                process = Process.objects.get(process_id=process_id)
                instance.process = process
            except Process.DoesNotExist:
                raise serializers.ValidationError({'process_id': '工艺不存在'})

        if 'irradiat_id' in validated_data:
            irradiat_id = validated_data.pop('irradiat_id')
            try:
                irradiat = IrrCondition.objects.get(irradiat_id=irradiat_id)
                instance.irradiat = irradiat
            except IrrCondition.DoesNotExist:
                raise serializers.ValidationError({'irradiat_id': '辐照条件不存在'})

        return super().update(instance, validated_data)

    def validate(self, data):
        """自定义验证"""
        # 验证实验温度
        ircreep_temp = data.get('ircreep_temp')
        if ircreep_temp is not None:
            try:
                ircreep_temp = float(ircreep_temp)
                if ircreep_temp < 0:
                    raise serializers.ValidationError({"ircreep_temp": "实验温度不能为负数"})
            except (ValueError, TypeError):
                raise serializers.ValidationError({"ircreep_temp": "实验温度必须是有效的数字"})
        
        # 验证实验时间
        ircreep_time = data.get('ircreep_time')
        if ircreep_time is not None:
            try:
                ircreep_time = float(ircreep_time)
                if ircreep_time < 0:
                    raise serializers.ValidationError({"ircreep_time": "实验时间不能为负数"})
            except (ValueError, TypeError):
                raise serializers.ValidationError({"ircreep_time": "实验时间必须是有效的数字"})
        
        # 验证断后伸长率
        irpercentage_elongation = data.get('irpercentage_elongation')
        if irpercentage_elongation is not None:
            try:
                irpercentage_elongation = float(irpercentage_elongation)
                if irpercentage_elongation < 0:
                    raise serializers.ValidationError({"irpercentage_elongation": "断后伸长率不能为负数"})
                elif irpercentage_elongation > 100:
                    raise serializers.ValidationError({"irpercentage_elongation": "断后伸长率不能大于100%"})
            except (ValueError, TypeError):
                raise serializers.ValidationError({"irpercentage_elongation": "断后伸长率必须是有效的数字"})
        
        return data 

class HardeningSerializer(serializers.ModelSerializer):
    """Serializer for the existing irradiation-hardening records."""
    material_id = serializers.PrimaryKeyRelatedField(
        source='material', queryset=Material.objects.all(), write_only=True
    )
    process_id = serializers.PrimaryKeyRelatedField(
        source='process', queryset=Process.objects.all(), write_only=True
    )
    irradiat_id = serializers.PrimaryKeyRelatedField(
        source='irradiat', queryset=IrrCondition.objects.all(), write_only=True
    )
    document_id = serializers.PrimaryKeyRelatedField(
        source='document', queryset=Document.objects.all(), write_only=True
    )
    material = serializers.SerializerMethodField(read_only=True)
    process = serializers.SerializerMethodField(read_only=True)
    irradiat = serializers.SerializerMethodField(read_only=True)
    document = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Hardening
        fields = [
            'hardening_id',
            'material_id',
            'process_id',
            'irradiat_id',
            'document_id',
            'material',
            'process',
            'irradiat',
            'document',
            'phase_structure',
            'pre_hv',
            'post_hv',
            'delta_hv',
            'entry_time',
            'modify_time',
        ]
        read_only_fields = ['hardening_id', 'entry_time', 'modify_time']

    def get_material(self, obj):
        return {
            'material_id': obj.material_id,
            'material_name': obj.material.material_name,
        }

    def get_process(self, obj):
        return {
            'process_id': obj.process_id,
            'fabrication': obj.process.fabrication,
        }

    def get_irradiat(self, obj):
        return {
            'irradiat_id': obj.irradiat_id,
            'irradiat_type': obj.irradiat.irradiat_type,
        }

    def get_document(self, obj):
        return {
            'document_id': obj.document_id,
            'doc_name': obj.document.doc_name,
            'doc_doi': obj.document.doc_doi,
            'doc_url': obj.document.doc_url,
        }

    def validate_phase_structure(self, value):
        if value is None:
            return value
        value = value.strip()
        return value or None


class DocumentSerializer(serializers.ModelSerializer):
    """参考文献序列化器"""
    class Meta:
        model = Document
        fields = [
            'document_id',
            'doc_name',
            'doc_doi',
            'doc_url',
            'entry_time',
            'modify_time'
        ]
        read_only_fields = ['document_id', 'entry_time', 'modify_time']

    def validate(self, data):
        """自定义验证"""
        import logging
        logger = logging.getLogger(__name__)
        
        # 记录接收到的数据
        logger.debug("Validating document fields: %s", sorted(data.keys()))
        
        # 验证文献名称
        doc_name = data.get('doc_name')
        if not doc_name or not doc_name.strip():
            logger.error("文献名称为空")
            raise serializers.ValidationError({"doc_name": "文献名称不能为空"})
        
        # 验证DOI号
        doc_doi = data.get('doc_doi')
        if not doc_doi or not doc_doi.strip():
            logger.error("DOI号为空")
            raise serializers.ValidationError({"doc_doi": "文献DOI号不能为空"})
        
        # 验证URL
        doc_url = data.get('doc_url')
        if not doc_url or not doc_url.strip():
            logger.error("URL为空")
            raise serializers.ValidationError({"doc_url": "在线链接不能为空"})
        
        # 确保URL格式正确 - 更宽松的处理
        if doc_url:
            # 确保是字符串类型
            doc_url = str(doc_url).strip()
            if not doc_url.startswith(('http://', 'https://')):
                logger.info(f"自动添加URL前缀，原URL: {doc_url}")
                data['doc_url'] = 'https://' + doc_url
                logger.info(f"处理后的URL: {data['doc_url']}")
        
        # 记录验证通过的数据
        logger.debug("Document validation passed for fields: %s", sorted(data.keys()))
        return data 
