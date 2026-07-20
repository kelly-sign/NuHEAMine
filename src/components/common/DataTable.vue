<template>
  <div class="data-table">
    <div class="table-header">
      <div class="left-section">
        <slot name="header-left"></slot>
      </div>
      <div class="right-section">
        <slot name="header-right"></slot>
      </div>
    </div>

    <el-table
      v-bind="$attrs"
      :data="data"
      v-loading="loading"
      border
      style="width: 100%"
    >
      <slot></slot>
    </el-table>

    <div class="table-footer">
      <slot name="footer">
        <el-pagination
          v-if="showPagination"
          :current-page="currentPage"
          :page-size="pageSize"
          :total="total"
          @current-change="handleCurrentChange"
          @size-change="handleSizeChange"
          layout="total, sizes, prev, pager, next"
          :page-sizes="[10, 20, 50, 100]"
        />
      </slot>
    </div>
  </div>
</template>

<script setup>
defineProps({
  data: {
    type: Array,
    required: true
  },
  loading: {
    type: Boolean,
    default: false
  },
  showPagination: {
    type: Boolean,
    default: true
  },
  currentPage: {
    type: Number,
    default: 1
  },
  pageSize: {
    type: Number,
    default: 10
  },
  total: {
    type: Number,
    default: 0
  }
})

const emit = defineEmits(['update:currentPage', 'update:pageSize'])

const handleCurrentChange = (val) => {
  emit('update:currentPage', val)
}

const handleSizeChange = (val) => {
  emit('update:pageSize', val)
}
</script>

<style scoped>
.data-table {
  background-color: #fff;
  border-radius: 4px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #ebeef5;
}

.table-footer {
  padding: 16px;
  text-align: right;
  border-top: 1px solid #ebeef5;
}
</style> 