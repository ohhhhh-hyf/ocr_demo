# 分级知识目录的语义回卷与双视图可视化设计文档

## 1. 背景与目标

当前系统存在一个分级知识目录，例如：

```text
高等数学
├── 极限
│   ├── 数列极限
│   ├── 函数极限
│   ├── 极限运算法则
│   ├── 两个重要极限
│   └── 等价无穷小
├── 连续
│   ├── 连续定义
│   ├── 间断点
│   └── 连续函数性质
└── 导数
    ├── 导数定义
    ├── 求导法则
    ├── 高阶导数
    └── 隐函数求导
```

如果直接固定使用某一级目录进行可视化，会出现两个问题：

1. 一级节点过少时，信息粒度过粗。
2. 叶子节点过多时，信息粒度过细。

因此系统不应该固定使用“第一级”“第二级”或者“叶子节点”，而应该根据目录结构、节点权重和展示空间，动态挑选一组最适合展示的知识节点。

本文定义一种：

> **基于语义回卷（Semantic Roll-up）的自适应知识聚合策略**

并且最终同时提供两种互补视图：

- **横向条形图（Horizontal Bar Chart）**：用于清晰比较当前知识块的大小与排序。
- **Treemap（矩形树图）**：用于保留父子层级关系，并展示知识结构。

二者展示同一份聚合结果，但表达重点不同。

---

# 2. 核心设计原则

## 2.1 不固定目录层级

最终展示节点允许来自不同层级。

例如：

```text
数列极限       二级
函数极限       二级
极限运算法则   二级
连续           一级
导数           一级
积分           一级
```

这是允许的。

因为当前目标不是严格复现目录，而是：

> 在有限的可视化空间内，用尽可能少的节点表达尽可能多的有效知识信息。

---

## 2.2 “展开”和“回卷”是两个基本动作

每个目录节点有两种表现形式。

例如：

```text
极限 50%
├── 数列极限 12%
├── 函数极限 15%
├── 极限运算 13%
└── 等价无穷小 10%
```

### 收起状态

```text
极限 50%
```

### 展开状态

```text
数列极限      12%
函数极限      15%
极限运算      13%
等价无穷小    10%
```

因此整个动态算法本质上就是：

```text
信息太粗  -> 向下展开
信息太细  -> 向上回卷
```

---

## 2.3 “语义回卷”优先于“其他”

假设当前有：

```text
连续定义      2%
左右连续      1%
间断点        2%
```

它们拥有共同父节点：

```text
连续
```

不建议直接处理成：

```text
其他 5%
```

而应该优先回卷成：

```text
连续 5%
```

原因：

- “连续”具有明确语义。
- “其他”只是视觉聚合，没有知识意义。
- 后续还可以点击“连续”继续下钻。
- 可以保留原目录关系。

因此聚合优先级建议：

```text
父级回卷
    >
同语义节点聚合
    >
其他
```

“其他”应该是最后兜底，而不是第一选择。

---

# 3. 双视图整体架构

推荐最终页面结构：

```text
┌────────────────────────────────────────────────────────────┐
│                        知识结构总览                        │
├──────────────────────────────┬─────────────────────────────┤
│                              │                             │
│       横向条形图             │          Treemap            │
│                              │                             │
│  极限运算 █████████ 22%      │   ┌───────────────┐         │
│  函数极限 ████████  18%      │   │     极限      │         │
│  导数     ███████   16%      │   │  ┌────┬────┐ │         │
│  连续     ██████    14%      │   │  │函数│运算│ │         │
│  积分     █████     12%      │   │  └────┴────┘ │         │
│                              │   └───────────────┘         │
│                              │                             │
└──────────────────────────────┴─────────────────────────────┘
```

两者职责不同。

---

# 4. 横向条形图的职责

横向条形图主要回答：

> 哪些知识块最多、最重要、最薄弱或者最值得复习？

它强调：

- 大小比较
- 排名
- 精确值
- 长标签可读性

例如：

```text
极限运算法则       ████████████████████ 22%
函数极限           █████████████████    18%
导数               ███████████████      16%
连续               █████████████        14%
积分               ███████████          12%
数列极限           █████████            10%
等价无穷小         ████████              8%
```

推荐始终按 value 从大到小排序。

如果知识块较多，例如 8～15 个，横向条形图仍然能保持较好可读性。

---

# 5. Treemap 的职责

Treemap 主要回答：

> 这些知识块在整个知识结构中属于哪里？

它强调：

- 父子关系
- 知识层级
- 面积占比
- 结构聚类

例如：

```text
高等数学
├── 极限 55
│   ├── 数列极限 12
│   ├── 函数极限 16
│   ├── 极限运算 17
│   └── 等价无穷小 10
├── 连续 8
├── 导数 22
└── 积分 15
```

Treemap 应该保留：

```text
极限
├── 数列极限
├── 函数极限
├── 极限运算
└── 等价无穷小
```

即使横向条形图最终把这些知识节点作为平级结果展示，Treemap 仍然可以借助 `parent_id` 恢复它们的结构归属。

---

# 6. 推荐数据模型

建议统一将知识目录转换为标准树节点。

```json
{
  "id": "limit",
  "name": "极限",
  "parent_id": "calculus",
  "depth": 1,
  "value": 55,
  "children": [
    {
      "id": "limit.sequence",
      "name": "数列极限",
      "parent_id": "limit",
      "depth": 2,
      "value": 12,
      "children": []
    }
  ]
}
```

建议至少包含：

| 字段 | 含义 |
|---|---|
| id | 节点唯一标识 |
| name | 展示名称 |
| parent_id | 父节点 |
| depth | 原目录深度 |
| value | 当前图表使用的权重 |
| children | 子节点 |
| path | 可选，完整目录路径 |
| metadata | 可选，附加属性 |

建议额外增加：

```json
{
  "leaf_count": 5,
  "has_children": true,
  "aggregated": false,
  "aggregation_type": null
}
```

其中：

- `aggregated=false`：节点直接来自原始知识目录。
- `aggregation_type="rollup"`：节点是父级回卷结果。
- `aggregation_type="other"`：节点为最终兜底“其他”。

---

# 7. value 到底代表什么

这是实现前必须确认的问题。

不要默认：

```text
一个知识点 = 一个单位
```

否则一个目录拆得更细，就会天然拥有更高占比。

推荐让 `value` 成为可配置指标。

## 7.1 内容分布模式

```text
value = 该知识节点对应内容 token 数
```

适合回答：

> 这份笔记主要写了什么？

---

## 7.2 重要度模式

```text
value = importance_score
```

适合回答：

> 哪些知识最重要？

---

## 7.3 薄弱度模式

```text
value = weakness_score
```

适合回答：

> 学生最薄弱的知识集中在哪里？

---

## 7.4 复习时间模式

```text
value = recommended_review_minutes
```

适合回答：

> 复习时间应该主要投入在哪里？

---

## 7.5 考试权重模式

```text
value = exam_weight
```

适合回答：

> 哪些知识对考试贡献最大？

---

# 8. 权重向上传播

对于父节点：

```text
极限
├── 数列极限 12
├── 函数极限 16
├── 极限运算 17
└── 等价无穷小 10
```

如果父节点没有单独 value，建议：

```text
父节点 value = 所有直接或叶子后代 value 之和
```

即：

```text
极限 = 12 + 16 + 17 + 10 = 55
```

推荐统一做一次后序遍历：

```python
def compute_value(node):
    if not node.children:
        return node.value

    node.value = sum(compute_value(child) for child in node.children)
    return node.value
```

如果父节点本身也有独立内容，需要提前明确：

```text
parent_self_value
```

否则容易发生重复计算。

推荐结构：

```json
{
  "self_value": 5,
  "children_value": 50,
  "value": 55
}
```

---

# 9. 动态策略的推荐参数

初版建议：

```python
TARGET_MIN = 4
TARGET_IDEAL = 6
TARGET_MAX = 8

MAX_SLICE_RATIO = 0.45
MIN_SLICE_RATIO = 0.05

MAX_RELATIVE_DEPTH = 3

MAX_BAR_ITEMS = 12
MAX_TREEMAP_VISIBLE_LEAVES = 20
```

注意：

这些值不是绝对规则，而是默认策略。

重点是：

```text
4～8 个主要块是优先目标，而不是强制目标。
```

如果信息结构不允许，就不要硬凑。

---

# 10. 动态聚合算法总体流程

完整流程：

```text
                    原始知识树
                        │
                        ▼
                 计算所有节点 value
                        │
                        ▼
                  选择当前根节点
                        │
                        ▼
               取根节点直接 children
                        │
                        ▼
                 初始候选节点集合
                        │
              ┌─────────┴─────────┐
              │                   │
         节点太少？          单节点过大？
              │                   │
             Yes                 Yes
              │                   │
         选择节点展开       判断是否值得展开
              │                   │
              └─────────┬─────────┘
                        ▼
                   更新候选集合
                        │
                        ▼
               是否存在大量小节点？
                        │
                       Yes
                        │
                        ▼
              优先尝试父级语义回卷
                        │
                        ▼
                再检查节点数量
                        │
        ┌───────────────┴────────────────┐
        │                                │
      合理                             仍过多
        │                                │
        ▼                                ▼
     输出结果                    语义聚合 / 其他
```

---

# 11. 第一步：初始化候选集

假设当前根节点是：

```text
高等数学
```

初始化：

```python
candidates = root.children
```

得到：

```text
极限 55
连续 8
导数 22
积分 15
```

不要一开始就把整棵树拍平成叶子节点。

---

# 12. 第二步：判断是否需要展开

## 条件 A：节点太少

如果：

```python
len(candidates) < TARGET_MIN
```

需要选择一个节点向下展开。

例如：

```text
高等数学
├── 极限 70
└── 导数 30
```

只有两个节点。

如果“极限”拥有丰富子节点，则展开。

---

## 条件 B：单一节点占比过大

例如：

```text
极限 60%
连续 20%
导数 12%
积分 8%
```

虽然已经 4 个节点，但：

```python
60% > MAX_SLICE_RATIO
```

说明“极限”过于笼统。

如果其子节点结构合理，则应该展开。

---

# 13. 不是所有大节点都应该展开

假设：

```text
积分 50%
├── 定积分 48%
└── 其他积分 2%
```

把：

```text
积分 50%
```

展开成：

```text
定积分 48%
其他积分 2%
```

信息并没有明显增加。

因此，需要一个 `expand_score`。

---

# 14. 展开价值 expand_score

推荐考虑四个因素：

```text
expand_score =
    节点占比
    × 子节点丰富度
    × 子节点均衡度
    × 语义有效性
```

初版可以简化。

## 14.1 节点占比

```python
ratio = node.value / total_value
```

越大的节点越值得进一步分析。

---

## 14.2 子节点数量

如果：

```text
children_count = 1
```

通常没必要展开。

推荐：

```python
child_count_score = min(len(children) / 4, 1)
```

---

## 14.3 子节点均衡度

例如：

### 情况 A

```text
25
25
25
25
```

非常值得展开。

### 情况 B

```text
97
1
1
1
```

不值得。

可以用简单方法：

```python
max_child_ratio = max(child.value) / node.value
balance_score = 1 - max_child_ratio
```

情况 A：

```text
1 - 0.25 = 0.75
```

情况 B：

```text
1 - 0.97 = 0.03
```

---

## 14.4 推荐初版公式

```python
expand_score = (
    ratio
    * child_count_score
    * balance_score
)
```

不要一开始过度复杂。

先让规则稳定，再根据真实数据调参。

---

# 15. 展开动作

假设候选集：

```text
极限 55
连续 8
导数 22
积分 15
```

展开“极限”：

```python
candidates.remove(limit_node)
candidates.extend(limit_node.children)
```

得到：

```text
数列极限 12
函数极限 16
极限运算 17
等价无穷小 10
连续 8
导数 22
积分 15
```

现在有 7 个节点。

这是非常理想的结果。

---

# 16. 第三步：小节点识别

对每一个候选节点：

```python
ratio = node.value / total_value
```

如果：

```python
ratio < MIN_SLICE_RATIO
```

标记为：

```text
small_node
```

例如：

```text
连续定义 2%
左右连续 1%
间断点 2%
```

---

# 17. 第四步：语义回卷

这是整个设计的核心。

假设候选集中存在：

```text
连续定义 2%
左右连续 1%
间断点 2%
```

并且它们拥有共同父节点：

```text
连续
```

则考虑：

```text
连续定义
左右连续
间断点
    ↓
连续
```

---

# 18. 语义回卷的基本条件

建议同时满足以下条件：

## 条件 1：同父节点

```python
same_parent = True
```

---

## 条件 2：至少两个兄弟节点参与

如果只有一个小节点：

```text
连续定义 2%
```

而：

```text
间断点 15%
```

不应该简单把整个“连续”回卷。

否则会把重要的“间断点”也吞掉。

---

## 条件 3：回卷后不会覆盖已经独立展示的重要兄弟节点

例如：

```text
连续
├── 连续定义 2%
├── 左右连续 2%
├── 间断点 20%
```

当前：

```text
连续定义 2%
左右连续 2%
间断点 20%
```

不能直接：

```text
连续 24%
```

因为“间断点”本身已经足够重要。

更好的方式是保留：

```text
间断点 20%
连续基础 4%
```

但如果不希望生成新语义节点，则直接：

```text
间断点 20%
其他连续内容 4%
```

这是比回卷整个父节点更安全的策略。

---

# 19. 完整父级回卷

只有当父节点下当前展示的有效子节点几乎全部属于小节点时，才直接恢复父节点。

例如：

```text
连续
├── 连续定义 2
├── 左右连续 1
└── 间断点 2
```

全部都小。

直接回卷：

```text
连续 5
```

---

# 20. 部分语义聚合

如果：

```text
连续
├── 连续定义 2
├── 左右连续 2
└── 间断点 15
```

推荐：

```text
间断点 15
连续基础 4
```

这里的：

```text
连续基础
```

属于“语义聚合节点”。

需要注意：

如果系统禁止生成新标题，可以退化为：

```text
间断点 15
连续（其他）4
```

建议优先：

```text
{父节点名称}·其他
```

而不是全局“其他”。

例如：

```text
连续·其他
```

明显优于：

```text
其他
```

---

# 21. 全局“其他”只作为最后兜底

推荐优先级：

```text
完整父级回卷
    ↓
父节点局部聚合
    ↓
相邻同语义聚合
    ↓
父级·其他
    ↓
全局其他
```

例如最终确实存在：

```text
数学史 1%
符号说明 1%
附加定理 1%
拓展阅读 1%
```

并且它们没有合理共同父节点，则：

```text
其他 4%
```

可以接受。

---

# 22. 节点数量过多时的处理

如果：

```python
len(candidates) > TARGET_MAX
```

不要马上删除。

按顺序：

### 第一步

寻找小节点兄弟集合。

### 第二步

尝试语义回卷。

### 第三步

计算回卷后节点数量。

### 第四步

如果依然过多，按照 value 排序。

### 第五步

保留重要节点，剩余节点按父级聚合。

最后实在无法压缩，才产生“其他”。

---

# 23. 推荐的整体评分函数

与其纯规则，还可以给当前方案计算质量分。

```text
quality =
    信息区分度
  - 视觉复杂度惩罚
  - 小节点惩罚
  - 巨大节点惩罚
  - 无语义聚合惩罚
```

初版不一定必须实现。

但可以保留接口：

```python
score_partition(candidates)
```

未来优化算法时使用。

---

# 24. 推荐算法伪代码

```python
def build_partition(root, config):
    compute_tree_values(root)

    total_value = root.value
    candidates = list(root.children)

    # 1. 不断处理“太粗”的节点
    while True:
        expandable = []

        for node in candidates:
            if not node.children:
                continue

            ratio = node.value / total_value

            score = compute_expand_score(node, total_value)

            if (
                len(candidates) < config.target_min
                or ratio > config.max_slice_ratio
            ):
                expandable.append((score, node))

        if not expandable:
            break

        expandable.sort(reverse=True, key=lambda x: x[0])
        _, node = expandable[0]

        new_count = (
            len(candidates)
            - 1
            + len(node.children)
        )

        if new_count > config.max_expand_candidate_count:
            break

        candidates.remove(node)
        candidates.extend(node.children)

    # 2. 处理过细节点
    candidates = semantic_rollup(
        candidates=candidates,
        total_value=total_value,
        min_ratio=config.min_slice_ratio,
        target_max=config.target_max,
    )

    # 3. 最终兜底
    candidates = final_compaction(
        candidates,
        target_max=config.target_max
    )

    return normalize_partition(candidates)
```

---

# 25. semantic_rollup 伪代码

```python
def semantic_rollup(
    candidates,
    total_value,
    min_ratio,
    target_max,
):
    while True:
        if len(candidates) <= target_max:
            break

        small_nodes = [
            node
            for node in candidates
            if node.value / total_value < min_ratio
        ]

        if not small_nodes:
            break

        groups = group_by_parent(small_nodes)

        best_group = choose_best_rollup_group(groups)

        if not best_group:
            break

        parent = best_group.parent

        all_visible_children = [
            node
            for node in candidates
            if node.parent_id == parent.id
        ]

        # 如果父节点当前所有可见子节点都属于回卷集合
        if set(all_visible_children) == set(best_group.nodes):
            for node in best_group.nodes:
                candidates.remove(node)

            candidates.append(
                make_rollup_parent(parent)
            )

        else:
            # 只聚合其中的小节点
            for node in best_group.nodes:
                candidates.remove(node)

            candidates.append(
                make_partial_rollup_node(
                    parent=parent,
                    nodes=best_group.nodes
                )
            )

    return candidates
```

---

# 26. 推荐输出结构

最终不要只给图表：

```json
[
  {
    "name": "函数极限",
    "value": 16
  }
]
```

应该输出：

```json
{
  "root": {
    "id": "calculus",
    "name": "高等数学"
  },
  "metric": "content_weight",
  "total_value": 100,
  "items": [
    {
      "id": "limit.sequence",
      "name": "数列极限",
      "value": 12,
      "ratio": 0.12,
      "depth": 2,
      "parent_id": "limit",
      "source_node_ids": [
        "limit.sequence"
      ],
      "aggregation_type": "none",
      "has_children": true
    },
    {
      "id": "continuous",
      "name": "连续",
      "value": 8,
      "ratio": 0.08,
      "depth": 1,
      "parent_id": "calculus",
      "source_node_ids": [
        "continuous.definition",
        "continuous.point",
        "continuous.property"
      ],
      "aggregation_type": "rollup",
      "has_children": true
    }
  ]
}
```

这样前端可以同时渲染：

- 横向条形图
- Treemap
- 点击下钻
- tooltip
- breadcrumb
- 聚合来源说明

---

# 27. 横向条形图的数据处理

横向条形图直接使用聚合后的 `items`。

排序：

```python
items = sorted(
    items,
    key=lambda x: x["value"],
    reverse=True,
)
```

示例：

```text
极限运算       17%
函数极限       16%
积分           15%
导数           22%
数列极限       12%
等价无穷小     10%
连续            8%
```

实际渲染前排序：

```text
导数           22%
极限运算       17%
函数极限       16%
积分           15%
数列极限       12%
等价无穷小     10%
连续            8%
```

---

# 28. 横向条形图建议交互

推荐：

### Hover

显示：

```text
函数极限
占比：16%
原始权重：1600 tokens
目录层级：2
父级：极限
```

如果节点是语义回卷：

```text
连续
占比：8%
由以下内容聚合：
- 连续定义
- 间断点
- 连续函数性质
```

---

### Click

如果：

```text
has_children = true
```

点击后：

```text
当前 root = clicked_node
```

重新运行：

```python
build_partition(clicked_node)
```

然后两个图同步刷新。

---

# 29. Treemap 不应该简单使用“扁平 items”

这是非常关键的一点。

横向条形图可以扁平显示。

Treemap 应该尽可能恢复层级。

例如最终 items：

```text
数列极限
函数极限
极限运算
等价无穷小
连续
导数
积分
```

Treemap 可以恢复为：

```text
高等数学
├── 极限
│   ├── 数列极限
│   ├── 函数极限
│   ├── 极限运算
│   └── 等价无穷小
├── 连续
├── 导数
└── 积分
```

即：

> 横向条形图展示“当前有效知识块”
>
> Treemap 展示“这些有效知识块在知识树中的结构位置”。

---

# 30. Treemap 数据构建策略

输入：

```json
[
  {
    "id": "limit.sequence",
    "parent_id": "limit"
  },
  {
    "id": "limit.function",
    "parent_id": "limit"
  },
  {
    "id": "continuous",
    "parent_id": "calculus"
  }
]
```

构造：

```json
{
  "name": "高等数学",
  "children": [
    {
      "name": "极限",
      "children": [
        {
          "name": "数列极限",
          "value": 12
        },
        {
          "name": "函数极限",
          "value": 16
        }
      ]
    },
    {
      "name": "连续",
      "value": 8
    }
  ]
}
```

---

# 31. Treemap 的中间父节点可以作为“结构节点”

例如：

```text
极限
```

虽然最终横向条形图中并没有“极限 55%”这一条，但 Treemap 仍然可以保留：

```text
极限
```

作为容器节点。

它只承担：

```text
层级分组
```

不作为额外 value 重复计算。

---

# 32. 防止 Treemap 重复计算

错误：

```text
极限 value=55
├── 数列极限 12
├── 函数极限 16
├── 极限运算 17
└── 等价无穷小 10
```

如果图表库同时对父 value 和子 value 求面积，可能重复。

推荐：

### 中间结构节点

```json
{
  "name": "极限",
  "children": [...]
}
```

不设置 value。

### 叶子展示节点

设置：

```json
{
  "name": "函数极限",
  "value": 16
}
```

---

# 33. 两个图必须联动

推荐状态：

```javascript
{
  currentRootId,
  selectedNodeId,
  hoveredNodeId,
  partitionItems
}
```

---

## Hover 联动

用户 hover：

```text
函数极限
```

则：

- 横向条形图高亮“函数极限”
- Treemap 同时高亮“函数极限”

---

## Click 联动

用户点击：

```text
极限
```

或者某个有 children 的知识节点。

执行：

```text
currentRoot = 极限
```

后端或前端重新调用：

```python
build_partition(limit_node)
```

两个图一起变成：

```text
数列极限
函数极限
极限运算
两个重要极限
等价无穷小
```

---

# 34. Breadcrumb 面包屑

强烈建议增加：

```text
高等数学 > 极限 > 函数极限
```

用户可以点击任意层级返回。

否则多次 drill-down 后容易失去位置感。

---

# 35. 一个完整示例

## 原始目录

```text
高等数学 100
├── 极限 55
│   ├── 数列极限 12
│   ├── 函数极限 16
│   ├── 极限运算 17
│   └── 等价无穷小 10
├── 连续 8
│   ├── 连续定义 2
│   ├── 间断点 3
│   └── 连续函数性质 3
├── 导数 22
└── 积分 15
```

---

## 第一轮

```text
极限 55
连续 8
导数 22
积分 15
```

候选数：

```text
4
```

但是：

```text
极限 = 55%
```

超过：

```text
MAX_SLICE_RATIO = 45%
```

所以尝试展开“极限”。

---

## 第二轮

```text
数列极限 12
函数极限 16
极限运算 17
等价无穷小 10
连续 8
导数 22
积分 15
```

共：

```text
7
```

没有特别小的节点。

最终接受。

---

# 36. 最终横向条形图

```text
导数           ██████████████████████ 22%
极限运算       █████████████████      17%
函数极限       ████████████████       16%
积分           ███████████████        15%
数列极限       ████████████           12%
等价无穷小     ██████████             10%
连续           ████████                8%
```

---

# 37. 最终 Treemap

结构：

```text
高等数学
├── 极限
│   ├── 数列极限 12
│   ├── 函数极限 16
│   ├── 极限运算 17
│   └── 等价无穷小 10
├── 连续 8
├── 导数 22
└── 积分 15
```

这里：

```text
极限
```

只是容器，不额外占 55。

它的面积自然由四个孩子之和决定。

---

# 38. 再看一个语义回卷例子

原始目录：

```text
高等数学
├── 极限
│   ├── 数列极限 20
│   └── 函数极限 22
├── 连续
│   ├── 连续定义 2
│   ├── 左右连续 1
│   └── 间断点 2
├── 导数
│   ├── 导数定义 18
│   └── 求导法则 17
└── 积分 18
```

如果全部展开：

```text
数列极限 20
函数极限 22
连续定义 2
左右连续 1
间断点 2
导数定义 18
求导法则 17
积分 18
```

共 8 个。

其中三个连续相关节点：

```text
2
1
2
```

均低于：

```text
MIN_SLICE_RATIO = 5%
```

由于它们：

- 同父
- 全部都是小节点
- 没有重要兄弟节点需要保留

因此执行语义回卷：

```text
连续定义 2
左右连续 1
间断点 2
    ↓
连续 5
```

最终：

```text
数列极限 20
函数极限 22
连续 5
导数定义 18
求导法则 17
积分 18
```

共 6 个。

这就是非常理想的结果。

---

# 39. Treemap 对回卷节点的展示

如果“连续”已经被回卷：

```text
连续 5
```

Treemap 默认显示：

```text
连续
```

而不是继续显示：

```text
连续定义
左右连续
间断点
```

但是用户点击“连续”后，可以重新进入该节点：

```text
连续
├── 连续定义
├── 左右连续
└── 间断点
```

重新计算当前局部视图。

---

# 40. 横向条形图与 Treemap 的功能分工

建议明确：

## 横向条形图

回答：

```text
谁最大？
谁最小？
谁排前面？
各知识点具体是多少？
```

---

## Treemap

回答：

```text
这些知识属于哪个父级？
知识结构如何分布？
哪些内容属于同一主题？
```

---

# 41. 不建议两个图完全重复

如果两个图都只是：

```text
A
B
C
D
```

那没有意义。

推荐：

### Bar

扁平 + 排序：

```text
导数
极限运算
函数极限
积分
数列极限
等价无穷小
连续
```

### Treemap

按结构组织：

```text
极限
├── 数列极限
├── 函数极限
├── 极限运算
└── 等价无穷小

连续
导数
积分
```

这样二者互补。

---

# 42. 推荐后端 API

例如：

```http
POST /api/knowledge/visualization
```

请求：

```json
{
  "root_id": "calculus",
  "metric": "content_weight",
  "target_min": 4,
  "target_max": 8
}
```

响应：

```json
{
  "root": {
    "id": "calculus",
    "name": "高等数学"
  },
  "metric": "content_weight",
  "total_value": 100,
  "partition": [
    {
      "id": "derivative",
      "name": "导数",
      "value": 22,
      "ratio": 0.22,
      "parent_id": "calculus",
      "aggregation_type": "none"
    }
  ],
  "treemap": {
    "name": "高等数学",
    "children": []
  },
  "breadcrumb": [
    {
      "id": "calculus",
      "name": "高等数学"
    }
  ]
}
```

---

# 43. 推荐代码模块拆分

建议不要把所有逻辑塞一个函数。

```text
knowledge_visualization/
├── models.py
├── tree_metrics.py
├── partition.py
├── rollup.py
├── expand.py
├── treemap_builder.py
├── bar_builder.py
├── config.py
└── tests/
```

---

## models.py

负责：

```text
KnowledgeNode
PartitionItem
VisualizationResult
```

---

## tree_metrics.py

负责：

```text
计算 value
计算 ratio
计算 leaf_count
计算节点统计信息
```

---

## expand.py

负责：

```text
compute_expand_score
choose_expand_node
expand_node
```

---

## rollup.py

负责：

```text
group_small_nodes_by_parent
semantic_rollup
partial_rollup
make_other_group
```

---

## partition.py

负责核心编排：

```text
build_partition
```

---

## treemap_builder.py

负责：

```text
partition -> hierarchy
```

---

## bar_builder.py

负责：

```text
partition -> sorted flat list
```

---

# 44. 推荐配置对象

```python
from dataclasses import dataclass


@dataclass
class PartitionConfig:
    target_min: int = 4
    target_ideal: int = 6
    target_max: int = 8

    max_slice_ratio: float = 0.45
    min_slice_ratio: float = 0.05

    max_relative_depth: int = 3
    max_bar_items: int = 12
    max_treemap_visible_leaves: int = 20
```

---

# 45. 边界情况

## 45.1 只有一个节点

```text
极限
```

如果它有 children：

```text
自动展开。
```

如果没有：

```text
直接显示一个条形项。
```

不要人为凑数量。

---

## 45.2 只有两个叶子节点

直接：

```text
A
B
```

不要制造“其他”。

---

## 45.3 一级节点已经有 6 个且比例合理

不展开。

---

## 45.4 一级节点 6 个，但其中一个占 80%

检查该节点是否值得展开。

---

## 45.5 节点 15 个，但都非常重要

不要为了 `TARGET_MAX=8` 强行损失信息。

可以允许：

```text
横向条形图展示 Top 12 + 剩余聚合
```

Treemap 可以展示更多。

因此：

> `partition` 和两个图表的“最终可见数量”可以允许略微不同。

但二者应共享同一个语义聚合基础。

---

# 46. 推荐的高级策略：主集合 + 扩展集合

可以输出：

```json
{
  "primary_items": [],
  "secondary_items": []
}
```

其中：

### primary_items

适合横向条形图：

```text
最多 8～12 个
```

### secondary_items

用于 Treemap 内部展开：

```text
允许更多知识点
```

这样：

- Bar 保持简洁。
- Treemap 保留更丰富结构。

---

# 47. 推荐最终 UX

页面：

```text
知识分布

[ 内容分布 ▼ ]

高等数学 > 极限

┌─────────────────────────┬─────────────────────────┐
│       知识重点排名       │        知识结构         │
│                         │                         │
│ 函数极限      28%       │      Treemap            │
│ 极限运算      24%       │                         │
│ 数列极限      20%       │                         │
│ 等价无穷小    18%       │                         │
│ 重要极限      10%       │                         │
└─────────────────────────┴─────────────────────────┘
```

顶部可以切换 metric：

```text
内容分布
知识重要度
薄弱度
复习时间
考试权重
```

---

# 48. 推荐 Tooltip

统一：

```text
函数极限

占比：16%
权重：1600 tokens
父级：极限
目录层级：2
子知识点：4

点击查看详情
```

对于 rollup：

```text
连续

占比：5%
类型：语义回卷

由以下内容聚合：
- 连续定义
- 左右连续
- 间断点

点击展开
```

---

# 49. 测试案例

至少覆盖以下测试。

## Case 1：一级只有 1 个节点

预期：

```text
向下展开
```

---

## Case 2：一级 3 个节点

预期：

```text
根据 expand_score 展开最有意义节点
```

---

## Case 3：一级 6 个且均衡

预期：

```text
直接输出
```

---

## Case 4：一级 5 个但一个占 70%

预期：

```text
展开大节点
```

---

## Case 5：展开后出现多个同父小节点

预期：

```text
语义回卷
```

---

## Case 6：小节点拥有重要兄弟节点

预期：

```text
不能整个父级回卷
```

使用局部聚合。

---

## Case 7：无法语义聚合

预期：

```text
父级·其他
```

---

## Case 8：完全没有共同语义

预期：

```text
最终才使用全局其他
```

---

## Case 9：所有节点几乎一样大，数量 12

预期：

```text
Bar 可以展示 12 个
Treemap 保留层级
不强制压成 6 个
```

---

# 50. 最重要的实现约束

Codex 实现时需要遵守以下原则。

## 原则 1

不要固定使用某一级目录。

---

## 原则 2

允许最终结果包含混合层级节点。

---

## 原则 3

任何聚合都必须可追溯。

必须保留：

```text
source_node_ids
```

---

## 原则 4

不要默认所有小节点都进入“其他”。

---

## 原则 5

优先父级语义回卷。

---

## 原则 6

Treemap 不要直接使用 Bar 的扁平排序结构。

Treemap 必须恢复目录父子关系。

---

## 原则 7

两个图共享：

```text
selectedNode
hoveredNode
currentRoot
```

实现联动。

---

## 原则 8

点击节点后重新以该节点为 root 做局部聚合，而不是简单前端放大。

---

# 51. MVP 推荐实现顺序

建议 Codex 分阶段实现。

## Phase 1

实现：

```text
标准 KnowledgeNode
value 递归计算
build_partition
```

先不做复杂评分。

规则：

```text
少 -> 展开最大节点
大节点 >45% -> 展开
小节点同父 -> 回卷
```

---

## Phase 2

增加：

```text
expand_score
```

防止无意义展开。

---

## Phase 3

增加：

```text
partial semantic rollup
```

支持：

```text
连续·其他
```

---

## Phase 4

增加：

```text
Bar + Treemap 双视图
```

---

## Phase 5

增加：

```text
hover 联动
click drill-down
breadcrumb
```

---

## Phase 6

基于真实数据调参。

重点观察：

```text
TARGET_MAX
MAX_SLICE_RATIO
MIN_SLICE_RATIO
expand_score
```

---

# 52. 最终一句话定义

整个功能可以定义为：

> 系统不按照固定目录层级生成知识图，而是根据知识节点权重、层级结构和视觉复杂度动态展开大节点、回卷同语义小节点，生成一组可追溯的自适应知识块；横向条形图负责展示这些知识块的大小与排名，Treemap 负责展示它们在原始知识树中的层级与结构，并通过点击节点实现同步下钻。

---

# 53. Codex 任务描述建议

可以直接将下面这段作为开发任务：

```text
请实现一个分级知识目录的自适应可视化聚合模块。

要求：

1. 输入是树形 KnowledgeNode。
2. 每个节点包含 id/name/parent_id/value/children。
3. 不固定使用某一级目录。
4. 从当前 root.children 开始生成候选集合。
5. 当候选过少或单节点占比过大时，动态向下展开。
6. 展开节点需要考虑子节点数量和分布，避免无意义展开。
7. 当候选节点过多或存在多个小节点时，优先对同父节点进行 semantic roll-up。
8. 如果父节点下同时存在重要节点与多个小节点，只聚合小节点，不吞并重要节点。
9. 全局“其他”只能作为最后兜底。
10. 所有聚合节点必须保留 source_node_ids，保证可追溯。
11. 输出统一 partition 数据。
12. 基于 partition 生成横向条形图数据。
13. 基于 partition + 原始目录 parent_id 恢复 Treemap 层级。
14. Bar 按 value 从大到小排序。
15. Treemap 保留父子结构，不重复计算父节点 value。
16. 支持 currentRoot 下钻。
17. 点击任意有子节点的节点后，以它作为新 root 重新运行聚合算法。
18. 支持 breadcrumb 返回上层。
19. 横向条形图与 Treemap 共用 hoveredNodeId / selectedNodeId，实现联动。
20. 请为聚合算法编写单元测试，至少覆盖本文“测试案例”章节中的场景。
```
