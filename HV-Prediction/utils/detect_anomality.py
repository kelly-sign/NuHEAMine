import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors

def detect_feature_label_anomalies(df, feature_columns, label_column,n_neighbors=5, threshold=2.5):
    """
    基于特征空间近邻与标签相对变化的异常检测（两遍统计，稳定标准化）
    """
    # ---- 0) 基本检查 ----
    if len(df) < 3:
        return {
            'anomaly_indices': [],
            'anomaly_df': df.iloc[[]],
            'total_samples': len(df),
            'anomaly_count': 0,
            'anomaly_ratio': 0.0,
            'anomalies_info': [],
            'global_avg_relative_change': 0.0,
            'global_std_relative_change': 0.0,
            'feature_columns': feature_columns,
            'label_column': label_column,
            'threshold_used': threshold
        }

    X = df[feature_columns].to_numpy(dtype=float)
    y = df[label_column].to_numpy(dtype=float)

    # ---- 1) 稳定标准化（防止除 0）----
    means = X.mean(axis=0)
    stds = X.std(axis=0)
    stds_safe = np.where(stds == 0, 1.0, stds)
    Xn = (X - means) / stds_safe

    # ---- 2) 邻居搜索（含自身，稍后去掉）----
    k = int(min(max(1, n_neighbors), len(df)-1))          # 边界保护
    nbrs = NearestNeighbors(n_neighbors=k+1, metric='euclidean')
    nbrs.fit(Xn)
    distances, indices = nbrs.kneighbors(Xn)

    # ---- 3) 第一遍：为每个样本计算 “平均相对变化/最大相对变化” ----
    per_point_avg = np.zeros(len(df), dtype=float)
    per_point_max = np.zeros(len(df), dtype=float)
    per_point_info = []

    for i in range(len(df)):
        neigh_idx = indices[i][1:k+1]                     # 去掉自身
        y_neigh = y[neigh_idx]

        # 相对变化：|yi - yj| / mean(|yi|, |邻居们|)
        denom = max(np.mean(np.abs(np.r_[y[i], y_neigh])), 1e-10)
        rel = np.abs(y[i] - y_neigh) / denom
        rel = rel[np.isfinite(rel)]

        if rel.size == 0:
            avg_rc, max_rc = 0.0, 0.0
        else:
            avg_rc, max_rc = rel.mean(), rel.max()

        per_point_avg[i] = avg_rc
        per_point_max[i] = max_rc
        per_point_info.append({
            'index': i,
            'orig_index': df.index[i],
            'features': X[i],
            'label_value': y[i],
            'avg_relative_change': avg_rc,
            'max_relative_change': max_rc,
            'neighbor_indices': neigh_idx,
            'neighbor_distances': distances[i][1:k+1],
        })

    # ---- 4) 第二遍：用“中位数 + threshold × MAD”做稳健阈值 ----
    median = float(np.median(per_point_avg))
    mad_raw = float(np.median(np.abs(per_point_avg - median)))
    mad = 1.4826 * mad_raw  # 正态一致性校正
    if mad == 0.0:
        mad = 1e-12  # 兜底，避免阈值失效

    cutoff = median + threshold * mad

    anomaly_mask = per_point_avg > cutoff
    anomaly_indices = np.where(anomaly_mask)[0].tolist()

    # 标记并构建返回
    for info in per_point_info:
        info['is_anomaly'] = bool(anomaly_mask[info['index']])

    result = {
        'anomaly_indices': anomaly_indices,
        'anomaly_df': df.iloc[anomaly_indices].copy(),
        'total_samples': len(df),
        'anomaly_count': len(anomaly_indices),
        'anomaly_ratio': (len(anomaly_indices) / len(df)) if len(df) else 0.0,
        'anomalies_info': per_point_info,
        # 记录稳健统计量，便于日志与调参
        'robust_median_avg_relative_change': median,
        'robust_mad_avg_relative_change': mad,
        'feature_columns': feature_columns,
        'label_column': label_column,
        'threshold_used': threshold,
        'threshold_type': 'median+MAD'
    }
    return result

# 改进的示例使用方式
if __name__ == "__main__":
    # 创建更合理的示例数据
    np.random.seed(42)
    n_samples = 100
    
    # 生成随机特征数据（3个特征）
    features = np.random.randn(n_samples, 3)
    
    # 生成标签（基于特征的线性关系，添加一些噪声）
    labels = 20 * features[:, 0] + 30 * features[:, 1] - 10 * features[:, 2] + np.random.normal(0, 5, n_samples)
    
    # 添加一些明显的异常点
    anomaly_indices = [10, 25, 60, 85]
    labels[anomaly_indices] += 200  # 使这些点的标签异常高
    
    # 创建DataFrame
    df = pd.DataFrame(features, columns=['feature1', 'feature2', 'feature3'])
    df['target_label'] = labels
    
    print("数据统计信息:")
    print(f"标签范围: [{labels.min():.2f}, {labels.max():.2f}]")
    print(f"标签均值: {labels.mean():.2f}")
    print(f"标签标准差: {labels.std():.2f}")
    print(f"预设异常点索引: {anomaly_indices}")
    print(f"预设异常点标签值: {labels[anomaly_indices]}")
    
    # 使用函数检测异常点
    result = detect_feature_label_anomalies(
        df=df,
        feature_columns=['feature1', 'feature2', 'feature3'],
        label_column='target_label',
        n_neighbors=5,
        threshold=4.5
    )
    
    print(f"\n检测到 {result['anomaly_count']} 个异常点")
    print("异常点索引:", result['anomaly_indices'])
    print("预设异常点是否被检测到:", set(anomaly_indices).issubset(result['anomaly_indices']))
    
    # 显示统计信息
    print(f"\n统计信息:")
    print(f"总样本数: {result['total_samples']}")
    print(f"异常点比例: {result['anomaly_ratio']:.3f}")
    print(f"全局平均相对变化: {result['global_avg_relative_change']:.3f}")
    print(f"全局相对变化标准差: {result['global_std_relative_change']:.3f}")
    print(f"使用的阈值: {result['threshold_used']} 倍标准差")
    
    # 显示详细的异常点信息
    if result['anomaly_count'] > 0:
        print("\n异常点详细信息:")
        for idx in result['anomaly_indices']:
            info = next(item for item in result['anomalies_info'] if item['index'] == idx)
            print(f"索引 {idx}: 标签值={info['label_value']:.2f}, "
                  f"平均相对变化={info['avg_relative_change']:.2f}, "
                  f"最大相对变化={info['max_relative_change']:.2f}")
    
    # 显示一些正常点的信息作为对比
    normal_indices = [i for i in range(min(5, len(df))) if i not in result['anomaly_indices']]
    if normal_indices:
        print(f"\n正常点对比信息 (前{len(normal_indices)}个):")
        for idx in normal_indices:
            info = next(item for item in result['anomalies_info'] if item['index'] == idx)
            print(f"索引 {idx}: 标签值={info['label_value']:.2f}, "
                  f"平均相对变化={info['avg_relative_change']:.2f}")
