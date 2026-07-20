from django.db import models

class Material(models.Model):
    """材料表"""
    material_id = models.AutoField(primary_key=True, verbose_name='材料ID')
    material_name = models.CharField(max_length=100, unique=True, verbose_name='材料名称')
    
    # 元素成分字段
    composition_al = models.FloatField(default=0, verbose_name='Al元素含量')
    composition_c = models.FloatField(default=0, verbose_name='C元素含量')
    composition_co = models.FloatField(default=0, verbose_name='Co元素含量')
    composition_cr = models.FloatField(default=0, verbose_name='Cr元素含量')
    composition_cu = models.FloatField(default=0, verbose_name='Cu元素含量')
    composition_fe = models.FloatField(default=0, verbose_name='Fe元素含量')
    composition_hf = models.FloatField(default=0, verbose_name='Hf元素含量')
    composition_mg = models.FloatField(default=0, verbose_name='Mg元素含量')
    composition_mn = models.FloatField(default=0, verbose_name='Mn元素含量')
    composition_mo = models.FloatField(default=0, verbose_name='Mo元素含量')
    composition_n = models.FloatField(default=0, verbose_name='N元素含量')
    composition_nb = models.FloatField(default=0, verbose_name='Nb元素含量')
    composition_ni = models.FloatField(default=0, verbose_name='Ni元素含量')
    composition_sc = models.FloatField(default=0, verbose_name='Sc元素含量')
    composition_si = models.FloatField(default=0, verbose_name='Si元素含量')
    composition_sn = models.FloatField(default=0, verbose_name='Sn元素含量')
    composition_ta = models.FloatField(default=0, verbose_name='Ta元素含量')
    composition_ti = models.FloatField(default=0, verbose_name='Ti元素含量')
    composition_v = models.FloatField(default=0, verbose_name='V元素含量')
    composition_w = models.FloatField(default=0, verbose_name='W元素含量')
    composition_y = models.FloatField(default=0, verbose_name='Y元素含量')
    composition_zn = models.FloatField(default=0, verbose_name='Zn元素含量')
    composition_zr = models.FloatField(default=0, verbose_name='Zr元素含量')

    # 时间字段
    entry_time = models.DateTimeField(auto_now_add=True, verbose_name='录入时间')
    modify_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'materials'
        verbose_name = '材料'
        verbose_name_plural = '材料'

    def __str__(self):
        return f"{self.material_id} - {self.material_name}"

class Process(models.Model):
    """工艺模型"""
    process_id = models.AutoField(primary_key=True, verbose_name='工艺ID')
    fabrication = models.CharField(max_length=100, verbose_name='制备工艺')
    homogenization = models.BooleanField(default=False, verbose_name='均匀化处理')
    homogenize_temp = models.FloatField(null=True, blank=True, verbose_name='均匀化温度')
    homogenize_time = models.FloatField(null=True, blank=True, verbose_name='均匀化时间')
    normalization = models.BooleanField(default=False, verbose_name='正火处理')
    normalize_temp = models.FloatField(null=True, blank=True, verbose_name='正火温度')
    normalize_time = models.FloatField(null=True, blank=True, verbose_name='正火时间')
    annealing = models.BooleanField(default=False, verbose_name='退火处理')
    annealing_temp = models.FloatField(null=True, blank=True, verbose_name='退火温度')
    annealing_time = models.FloatField(null=True, blank=True, verbose_name='退火时间')
    tempering = models.BooleanField(default=False, verbose_name='回火处理')
    tempering_temp = models.FloatField(null=True, blank=True, verbose_name='回火温度')
    tempering_time = models.FloatField(null=True, blank=True, verbose_name='回火时间')
    quenching = models.BooleanField(default=False, verbose_name='淬火处理')
    quenching_type = models.CharField(max_length=50, null=True, blank=True, verbose_name='淬火类型')
    quenching_temp = models.FloatField(null=True, blank=True, verbose_name='淬火温度')
    rolling = models.BooleanField(default=False, verbose_name='轧制处理')
    rolling_temp = models.FloatField(null=True, blank=True, verbose_name='轧制温度')
    reduction = models.FloatField(null=True, blank=True, verbose_name='压下量')
    entry_time = models.DateTimeField(auto_now_add=True, verbose_name='录入时间')
    modify_time = models.DateTimeField(auto_now=True, verbose_name='修改时间')

    class Meta:
        db_table = 'processes'
        verbose_name = '工艺'
        verbose_name_plural = '工艺'
        ordering = ['-entry_time']

    def __str__(self):
        return f"{self.process_id}-{self.fabrication}"

class RoomTempProperty(models.Model):
    """室温结构性能表"""
    rtproperty_id = models.AutoField(primary_key=True, verbose_name='结构ID')
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='room_temp_property', verbose_name='材料')
    process = models.ForeignKey(Process, on_delete=models.CASCADE, related_name='room_temp_property', verbose_name='工艺')
    phase_structure = models.CharField(max_length=100, null=True, blank=True, verbose_name='相结构')
    hardness_value = models.FloatField(null=True, blank=True, verbose_name='硬度')
    yield_strength_c = models.FloatField(null=True, blank=True, verbose_name='压缩屈服强度')
    yield_strength_t = models.FloatField(null=True, blank=True, verbose_name='拉伸屈服强度')
    ultimate_strength_c = models.FloatField(null=True, blank=True, verbose_name='极限压缩强度')
    ultimate_strength_t = models.FloatField(null=True, blank=True, verbose_name='极限拉伸强度')
    fracture_strain_c = models.FloatField(null=True, blank=True, verbose_name='压缩断裂应变')
    fracture_strain_t = models.FloatField(null=True, blank=True, verbose_name='拉伸断裂应变')
    entry_time = models.DateTimeField(auto_now_add=True, verbose_name='录入时间')
    modify_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'rtproperties'
        verbose_name = '室温结构性能'
        verbose_name_plural = '室温结构性能'

    def __str__(self):
        return f"{self.material.material_id}的室温结构性能"

class MaterialProperty(models.Model):
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)  # 性能名称
    value = models.FloatField()            # 性能值
    unit = models.CharField(max_length=20)  # 单位

    class Meta:
        db_table = 'material_properties' 

class HTProperty(models.Model):
    """高温力学性能表"""
    htproperty_id = models.AutoField(primary_key=True, verbose_name='力学ID')
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='ht_property', verbose_name='材料')
    process = models.ForeignKey(Process, on_delete=models.CASCADE, related_name='ht_property', verbose_name='工艺')
    test_type = models.CharField(max_length=50, verbose_name='测试类型')
    htproperty_temp = models.FloatField(verbose_name='测试温度')
    yield_strength = models.FloatField(null=True, blank=True, verbose_name='屈服强度')
    ultimate_strength = models.FloatField(null=True, blank=True, verbose_name='极限强度')
    fracture_strain = models.FloatField(null=True, blank=True, verbose_name='断裂应变')
    entry_time = models.DateTimeField(auto_now_add=True, verbose_name='录入时间')
    modify_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'htproperties'
        verbose_name = '高温力学性能'
        verbose_name_plural = '高温力学性能'

    def __str__(self):
        return f"{self.material.material_id}的高温力学性能"

class ImpTest(models.Model):
    """冲击测试表"""
    impact_id = models.AutoField(primary_key=True, verbose_name='冲击测试ID')
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='imp_test', verbose_name='材料')
    process = models.ForeignKey(Process, on_delete=models.CASCADE, related_name='imp_test', verbose_name='工艺')
    impact_temp = models.FloatField(null=True, blank=True, verbose_name='测试温度')
    impact_type = models.CharField(max_length=100, null=True, blank=True, verbose_name='冲击类型')
    impact_energy = models.FloatField(null=True, blank=True, verbose_name='冲击能量')
    absorbed_energy = models.FloatField(null=True, blank=True, verbose_name='吸收功')
    impact_tough_value = models.FloatField(null=True, blank=True, verbose_name='冲击韧性值')
    fracture_type = models.CharField(max_length=100, null=True, blank=True, verbose_name='断裂类型')
    entry_time = models.DateTimeField(auto_now_add=True, verbose_name='录入时间')
    modify_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'imptests'
        verbose_name = '冲击测试'
        verbose_name_plural = '冲击测试'

    def __str__(self):
        return f"{self.material.material_id}的冲击测试"

class CreTest(models.Model):
    """蠕变测试表"""
    creep_id = models.AutoField(primary_key=True, verbose_name='蠕变测试ID')
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='cre_test', verbose_name='材料')
    process = models.ForeignKey(Process, on_delete=models.CASCADE, related_name='cre_test', verbose_name='工艺')
    creep_temp = models.FloatField(null=True, blank=True, verbose_name='测试温度')
    creep_time = models.FloatField(null=True, blank=True, verbose_name='测试时间')
    initial_stress = models.FloatField(null=True, blank=True, verbose_name='初始应力')
    creep_rate = models.FloatField(null=True, blank=True, verbose_name='稳态蠕变速率')
    creep_limit = models.FloatField(null=True, blank=True, verbose_name='蠕变极限')
    creep_rupture_strength = models.FloatField(null=True, blank=True, verbose_name='蠕变持久强度')
    rupture_time = models.FloatField(null=True, blank=True, verbose_name='断裂时间')
    rupture_strength_limit = models.FloatField(null=True, blank=True, verbose_name='持久强度极限')
    percentage_elongation = models.FloatField(null=True, blank=True, verbose_name='断后伸长率')
    entry_time = models.DateTimeField(auto_now_add=True, verbose_name='录入时间')
    modify_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'cretests'
        verbose_name = '蠕变测试'
        verbose_name_plural = '蠕变测试'

    def __str__(self):
        return f"{self.material.material_id}的蠕变测试"

class FatTest(models.Model):
    """疲劳测试表"""
    fatigue_id = models.AutoField(primary_key=True, verbose_name='疲劳测试ID')
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='fat_test', verbose_name='材料')
    process = models.ForeignKey(Process, on_delete=models.CASCADE, related_name='fat_test', verbose_name='工艺')
    fatigue_method = models.CharField(max_length=100, null=True, blank=True, verbose_name='测试类型')
    stress_ratio = models.FloatField(null=True, blank=True, verbose_name='应力比')
    stress_range = models.FloatField(null=True, blank=True, verbose_name='应力幅')
    mean_stress = models.FloatField(null=True, blank=True, verbose_name='平均应力')
    loading_frequency = models.FloatField(null=True, blank=True, verbose_name='加载频率')
    environment_temp = models.FloatField(null=True, blank=True, verbose_name='环境温度')
    fatigue_life = models.FloatField(null=True, blank=True, verbose_name='疲劳寿命')
    fatigue_limit = models.FloatField(null=True, blank=True, verbose_name='疲劳极限')
    entry_time = models.DateTimeField(auto_now_add=True, verbose_name='录入时间')
    modify_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'fattests'
        verbose_name = '疲劳测试'
        verbose_name_plural = '疲劳测试'

    def __str__(self):
        return f"{self.material.material_id}的疲劳测试"

class IrrCondition(models.Model):
    """辐照条件表模型"""
    irradiat_id = models.AutoField(primary_key=True, verbose_name="辐照ID")
    irradiat_type = models.CharField(max_length=100, null=True, blank=True, verbose_name="辐照类型")
    irradiat_energy = models.FloatField(null=True, blank=True, verbose_name="粒子能量")
    irradiat_temp = models.FloatField(null=True, blank=True, verbose_name="辐照温度")
    irradiat_dose = models.FloatField(null=True, blank=True, verbose_name="辐照剂量")
    irradiat_fluence = models.CharField(max_length=100, null=True, blank=True, verbose_name="辐照注量")
    displac_damage = models.FloatField(null=True, blank=True, verbose_name="离位损伤")
    entry_time = models.DateTimeField(auto_now_add=True, verbose_name="录入时间")
    modify_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = 'irrconditions'
        verbose_name = '辐照条件'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"辐照条件 {self.irradiat_id}" 

class MicrostructureEvolution(models.Model):
    """微结构演化表模型"""
    microstructure_id = models.AutoField(primary_key=True, verbose_name="微结构ID")
    material = models.ForeignKey(Material, on_delete=models.CASCADE, verbose_name="材料")
    process = models.ForeignKey(Process, on_delete=models.CASCADE, verbose_name="工艺")
    irradiat = models.ForeignKey(IrrCondition, on_delete=models.CASCADE, verbose_name="辐照条件")
    he_bubble_diam = models.FloatField(null=True, blank=True, verbose_name="氦泡直径")
    he_bubble_dens = models.FloatField(null=True, blank=True, verbose_name="氦泡密度")
    swelling_rate = models.FloatField(null=True, blank=True, verbose_name="肿胀率")
    irradiat_hard = models.FloatField(null=True, blank=True, verbose_name="辐照硬化量")
    entry_time = models.DateTimeField(auto_now_add=True, verbose_name="录入时间")
    modify_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = 'microstructures'
        verbose_name = '微结构演化'
        verbose_name_plural = verbose_name
        ordering = ['-entry_time']

    def __str__(self):
        return f"微结构演化 {self.microstructure_id}" 

class Embrittlement(models.Model):
    """辐照脆化表模型"""
    embrittlement_id = models.AutoField(primary_key=True, verbose_name="辐照脆化ID")
    material = models.ForeignKey(Material, on_delete=models.CASCADE, verbose_name="材料")
    process = models.ForeignKey(Process, on_delete=models.CASCADE, verbose_name="工艺")
    irradiat = models.ForeignKey(IrrCondition, on_delete=models.CASCADE, verbose_name="辐照条件")
    dbtt = models.FloatField(null=True, blank=True, verbose_name="韧脆转变温度")
    dbtt_difference = models.FloatField(null=True, blank=True, verbose_name="韧脆转变温度变化")
    entry_time = models.DateTimeField(auto_now_add=True, verbose_name="录入时间")
    modify_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = 'embrittlements'
        verbose_name = '辐照脆化'
        verbose_name_plural = verbose_name
        ordering = ['-entry_time']

    def __str__(self):
        return f"辐照脆化 {self.embrittlement_id}" 

class IrrCreep(models.Model):
    """辐照蠕变表模型"""
    ircreep_id = models.AutoField(primary_key=True, verbose_name="辐照蠕变ID")
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='irr_creep', verbose_name="材料")
    process = models.ForeignKey(Process, on_delete=models.CASCADE, related_name='irr_creep', verbose_name="工艺")
    irradiat = models.ForeignKey(IrrCondition, on_delete=models.CASCADE, related_name='irr_creep', verbose_name="辐照条件")
    ircreep_temp = models.FloatField(null=True, blank=True, verbose_name="实验温度")
    ircreep_time = models.FloatField(null=True, blank=True, verbose_name="实验时间")
    irinitial_stress = models.FloatField(null=True, blank=True, verbose_name="初始应力")
    ircreep_rate = models.FloatField(null=True, blank=True, verbose_name="稳态蠕变速率")
    ircreep_limit = models.FloatField(null=True, blank=True, verbose_name="蠕变极限")
    ircreep_rupture_strength = models.FloatField(null=True, blank=True, verbose_name="蠕变持久强度")
    irrupture_time = models.FloatField(null=True, blank=True, verbose_name="断裂时间")
    irrupture_strength_limit = models.FloatField(null=True, blank=True, verbose_name="持久强度极限")
    irpercentage_elongation = models.FloatField(null=True, blank=True, verbose_name="断后伸长率")
    entry_time = models.DateTimeField(auto_now_add=True, verbose_name="录入时间")
    modify_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = 'irrcreeps'
        verbose_name = '辐照蠕变'
        verbose_name_plural = verbose_name
        ordering = ['-entry_time']

    def __str__(self):
        return f"辐照蠕变 {self.ircreep_id}" 

class Hardening(models.Model):
    """Map the existing irradiation-hardening table."""
    hardening_id = models.AutoField(primary_key=True, verbose_name='Irradiation hardening ID')
    material = models.ForeignKey(
        Material,
        on_delete=models.RESTRICT,
        related_name='hardenings',
        verbose_name='Material'
    )
    process = models.ForeignKey(
        Process,
        on_delete=models.RESTRICT,
        related_name='hardenings',
        verbose_name='Process'
    )
    irradiat = models.ForeignKey(
        IrrCondition,
        on_delete=models.RESTRICT,
        related_name='hardenings',
        verbose_name='Irradiation condition'
    )
    document = models.ForeignKey(
        'Document',
        on_delete=models.RESTRICT,
        related_name='hardenings',
        verbose_name='Reference document'
    )
    phase_structure = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='Phase structure'
    )
    pre_hv = models.FloatField(null=True, blank=True, verbose_name='Pre-irradiation hardness (HV)')
    post_hv = models.FloatField(null=True, blank=True, verbose_name='Post-irradiation hardness (HV)')
    delta_hv = models.FloatField(null=True, blank=True, verbose_name='Hardness change (HV)')
    entry_time = models.DateTimeField(auto_now_add=True, verbose_name='Entry time')
    modify_time = models.DateTimeField(auto_now=True, verbose_name='Modify time')

    class Meta:
        managed = False
        db_table = 'hardenings'
        verbose_name = 'Irradiation hardening'
        verbose_name_plural = verbose_name
        ordering = ['-entry_time']

    def __str__(self):
        return f"Irradiation hardening {self.hardening_id}"


class Document(models.Model):
    """参考文献表模型"""
    document_id = models.AutoField(primary_key=True, verbose_name="文献ID")
    doc_name = models.CharField(max_length=200, verbose_name="文献名称")
    doc_doi = models.CharField(max_length=100, verbose_name="文献DOI号")
    doc_url = models.CharField(max_length=500, verbose_name="在线链接")
    entry_time = models.DateTimeField(auto_now_add=True, verbose_name="录入时间")
    modify_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = 'documents'
        verbose_name = '参考文献'
        verbose_name_plural = verbose_name
        ordering = ['-entry_time']

    def __str__(self):
        return f"参考文献 {self.document_id} - {self.doc_name}" 
