# FreeCAD CLI

FreeCAD 命令行接口 - 为 AI 系统提供完整的 FreeCAD CAD 功能访问能力。

[English](README.md)

## 功能特性

- **完整 API 覆盖**: 支持 FreeCAD 所有核心模块 (Part, Sketcher, Draft, Arch, Mesh 等)
- **AI 友好输出**: 原生 JSON/YAML 格式输出，便于 AI 系统解析
- **自然语言解析**: 支持将自然语言命令转换为结构化 CLI 调用
- **批量操作**: 支持批量命令执行和事务处理
- **多格式导出**: 支持 STEP, STL, OBJ, IGES 等主流格式

## 安装

### 前置要求

- Python 3.8+
- FreeCAD 0.19+ (需要安装 FreeCAD Python 模块)
- Node.js 16+ (用于 npm 安装)

### npm 安装 (推荐)

```bash
npm install freecad-cli
npx freecad-cli --help
```

### pip 安装

```bash
pip install freecad-cli
freecad-cli --help
```

### 从源码安装

```bash
git clone https://github.com/MiniMax-AI/freecad-cli.git
cd freecad-cli
pip install -e .
```

## 快速开始

### 基本命令

```bash
# 查看帮助
freecad-cli --help

# 检查 FreeCAD 状态
freecad-cli info status

# 查看可用模块
freecad-cli info modules
```

### Part 模块 (零件建模)

```bash
# 创建立方体
freecad-cli part create --name MyBox --type Box --params '{"length": 10, "width": 10, "height": 5}'

# 创建圆柱体
freecad-cli part create --name MyCylinder --type Cylinder --params '{"radius": 5, "height": 20}'

# 创建球体
freecad-cli part create --name MySphere --type Sphere --params '{"radius": 8}'

# 列出所有 Part 对象
freecad-cli part list

# 查看对象信息
freecad-cli part info --name MyBox
```

### Sketch 模块 (草图)

```bash
# 创建草图
freecad-cli sketch create --name MySketch --plane XY

# 添加直线
freecad-cli sketch add-line --sketch MySketch --x1 0 --y1 0 --x2 10 --y2 10

# 添加圆
freecad-cli sketch add-circle --sketch MySketch --cx 5 --cy 5 --radius 3

# 列出所有草图
freecad-cli sketch list
```

### Draft 模块 (2D 绘制)

```bash
# 创建直线
freecad-cli draft line --name MyLine --x1 0 --y1 0 --z1 0 --x2 100 --y2 100 --z2 0

# 创建圆
freecad-cli draft circle --name MyCircle --radius 50

# 创建矩形
freecad-cli draft rectangle --name MyRect --length 80 --height 40

# 创建多边形
freecad-cli draft polygon --name MyHex --sides 6 --radius 30
```

### Arch 模块 (建筑)

```bash
# 创建墙体
freecad-cli arch wall --name MainWall --length 500 --width 20 --height 300

# 创建结构
freecad-cli arch structure --name Column --length 50 --width 50 --height 400

# 创建窗户
freecad-cli arch window --name Window1 --width 120 --height 150
```

### Mesh 模块 (网格)

```bash
# 创建规则网格
freecad-cli mesh create --name MyMesh --type RegularMesh --params '{"width": 10, "height": 10}'

# 创建三角形网格
freecad-cli mesh create --name TriMesh --type Triangle --params '{"points": [[0,0,0], [10,0,0], [5,10,0]]}'

# 从形状创建网格
freecad-cli mesh from-shape --name MeshFromShape --source MyBox --deflection 0.1

# 网格布尔运算 (并集)
freecad-cli mesh boolean --name MeshUnion --operation Union --object1 Mesh1 --object2 Mesh2

# 列出所有 Mesh 对象
freecad-cli mesh list
```

### Surface 模块 (曲面)

```bash
# 创建填充曲面
freecad-cli surface create --name MySurface --type Fill

# 创建扫掠曲面
freecad-cli surface create --name SweepSurface --type Sweep --params '{"sections": ["sketch1", "sketch2"]}'

# 创建放样曲面
freecad-cli surface create --name LoftSurface --type Loft --params '{"sections": ["sketch1", "sketch2"]}'

# 创建贝塞尔曲面
freecad-cli surface create --name BezierSurface --type Bezier

# 从边界创建曲面
freecad-cli surface from-edges --name SurfaceFromEdges --sketch MySketch
```

### PartDesign 模块 (零件设计)

```bash
# 创建 Body
freecad-cli partdesign create-body --name MyBody

# 创建 Pad (拉伸)
freecad-cli partdesign pad --name MyPad --body MyBody --sketch MySketch --length 20

# 创建 Pocket (切除)
freecad-cli partdesign pocket --name MyPocket --body MyBody --sketch MySketch --length 10

# 创建孔
freecad-cli partdesign hole --name MyHole --body MyBody --diameter 5 --depth 15

# 创建旋转体
freecad-cli partdesign revolution --name MyRevolution --body MyBody --sketch MySketch --angle 360

# 创建旋转切除 (Groove)
freecad-cli partdesign groove --name MyGroove --body MyBody --angle 360 --radius 10

# 创建圆角
freecad-cli partdesign fillet --name MyFillet --body MyBody --radius 2

# 创建倒角
freecad-cli partdesign chamfer --name MyChamfer --body MyBody --size 1
```

### TechDraw 模块 (工程图)

```bash
# 创建工程图页面
freecad-cli techdraw create-page --name DrawPage --template A4_Landscape

# 添加视图
freecad-cli techdraw add-view --page DrawPage --source MyPart --projection FirstAngle

# 添加尺寸标注
freecad-cli techdraw add-dimension --view View --type Horizontal

# 导出工程图
freecad-cli techdraw export --page DrawPage --filepath output/drawing.pdf --format PDF
```

### Spreadsheet 模块 (电子表格)

```bash
# 创建电子表格
freecad-cli spreadsheet create --name Params

# 设置单元格值
freecad-cli spreadsheet set-cell --sheet Params --cell A1 --value 10

# 设置公式
freecad-cli spreadsheet set-formula --sheet Params --cell B1 --formula "=A1*2"

# 链接到对象属性
freecad-cli spreadsheet link --sheet Params --object MyBox --property Length --cell A1
```

### Assembly 模块 (装配)

```bash
# 创建装配
freecad-cli assembly create --name MyAssembly

# 添加零件
freecad-cli assembly add-part --assembly MyAssembly --part Part1 --placement [0,0,0]

# 添加约束
freecad-cli assembly add-constraint --assembly MyAssembly --type Coincident --object1 Part1 --object2 Part2
```

### Path 模块 (CAM 加工)

```bash
# 创建加工任务
freecad-cli path create-job --name Job1 --base MyPart

# 添加操作
freecad-cli path add-operation --job Job1 --type Drill

# 导出 G-code
freecad-cli path export-gcode --job Job1 --filepath output/gcode.nc --post linuxcnc
```

### FEM 模块 (有限元分析)

```bash
# 创建分析
freecad-cli fem create-analysis --name Analysis --type static

# 添加材料
freecad-cli fem add-material --analysis Analysis --material Steel

# 添加边界条件
freecad-cli fem add-bc --analysis Analysis --type Fixed --object MyPart

# 运行分析
freecad-cli fem run --analysis Analysis
```

### Image 模块 (图像)

```bash
# 导入图像
freecad-cli image import --name MyImage --filepath photo.png

# 缩放图像
freecad-cli image scale --name MyImage --x 2.0 --y 2.0
```

### Material 模块 (材料)

```bash
# 创建材料
freecad-cli material create --name CustomSteel --density 7850 --youngs 210000 --poisson 0.3

# 获取标准材料
freecad-cli material get-standard --name Steel
```

### Inspection 模块 (检测)

```bash
# 创建检测
freecad-cli inspection create-check --name Check1 --object MyPart

# 测量距离
freecad-cli inspection measure-distance --object1 Part1 --object2 Part2
```

### 布尔运算

```bash
# 并集 (合并)
freecad-cli boolean fuse --name Union --object1 Box1 --object2 Box2

# 差集 (减去)
freecad-cli boolean cut --name Cut --object1 Box1 --object2 Cylinder1

# 交集 (共同部分)
freecad-cli boolean common --name Common --object1 Box1 --object2 Sphere1

# 截面
freecad-cli boolean section --name Section --object1 Box1 --object2 Plane1
```

### 导出

```bash
# 导出为 STEP
freecad-cli export step --filepath output/model.step

# 导出为 STL
freecad-cli export stl --filepath output/model.stl

# 导出为 OBJ
freecad-cli export obj --filepath output/model.obj

# 导出为 IGES
freecad-cli export iges --filepath output/model.iges
```

## 输出格式

### JSON 格式 (默认)

```json
{
  "status": "success",
  "timestamp": "2024-01-15T10:30:00",
  "message": "Part 'MyBox' 创建成功",
  "data": {
    "name": "MyBox",
    "type": "Box",
    "label": "MyBox",
    "bounding_box": {
      "x_min": 0,
      "x_max": 10,
      "y_min": 0,
      "y_max": 10,
      "z_min": 0,
      "z_max": 5
    }
  }
}
```

### 其他格式

```bash
# YAML 格式
freecad-cli --format yaml part create --name MyBox --type Box

# 表格格式
freecad-cli --format table object list

# 纯文本格式
freecad-cli --format text info status
```

## AI 集成

### Python API

```python
from freecad_cli import FreeCADWrapper, AICommandParser

# 初始化
wrapper = FreeCADWrapper(headless=True)
wrapper.initialize()

# 创建对象
result = wrapper.create_part("MyBox", "Box", {"length": 10, "width": 10, "height": 5})
print(result)

# 自然语言解析
parser = AICommandParser()
result = parser.parse("创建一个名为 TestBox 的立方体")
print(result)  # {'command_group': 'part', 'command': 'create', 'parameters': {...}}
```

### 批量操作

```python
from freecad_cli import FreeCADWrapper, BatchProcessor

wrapper = FreeCADWrapper()
processor = BatchProcessor(wrapper)
wrapper.initialize()

commands = [
    {"command_group": "part", "command": "create", "parameters": {"name": "Box1", "type": "Box"}},
    {"command_group": "part", "command": "create", "parameters": {"name": "Box2", "type": "Box"}},
    {"command_group": "boolean", "command": "fuse", "parameters": {"name": "Union", "object1": "Box1", "object2": "Box2"}},
]

results = processor.execute_batch(commands)
summary = processor.get_summary()
print(f"成功: {summary['success']}/{summary['total']}")
```

## 架构

```
freecad_cli/
├── __init__.py                # 包初始化
├── core.py                    # 主 CLI 入口和命令定义
├── formatter.py               # 输出格式化工具 (JSON/YAML/text/table)
├── freecad_integration.py     # FreeCAD API 包装器 (核心)
├── ai_integration.py          # AI 集成模块 (NL 解析)
├── decorators.py              # 装饰器和 NonEmptyString 验证
├── _mock.py                   # Mock 状态跟踪 (测试用)
├── _part.py                   # Part 模块 (Box, Cylinder, Sphere, ...)
├── _sketch.py                 # Sketch 模块 (草图、几何)
├── _draft.py                  # Draft 模块 (2D 绘制)
├── _arch.py                   # Arch 模块 (建筑信息模型)
├── _boolean.py                # Boolean 模块 (Fuse, Cut, Common, ...)
├── _mesh.py                   # Mesh 模块 (网格处理)
├── _surface.py                # Surface 模块 (曲面建模)
├── _partdesign.py             # PartDesign 模块 (Pad, Pocket, Hole, ...)
├── _export.py                 # Export 模块 (STEP, STL, OBJ, ...)
├── _techdraw.py               # TechDraw 模块 (工程图)
├── _spreadsheet.py            # Spreadsheet 模块 (电子表格)
├── _assembly.py               # Assembly 模块 (装配管理)
├── _path.py                   # Path 模块 (CAM 加工)
├── _fem.py                    # FEM 模块 (有限元分析)
├── _image.py                  # Image 模块 (图像处理)
├── _material.py               # Material 模块 (材料管理)
├── _inspection.py             # Inspection 模块 (检测测量)
└── __main__.py                # 直接运行入口
```

## 支持的模块

| 模块 | 功能 | 状态 |
|------|------|------|
| Part | 零件建模、基础几何体 | ✅ |
| Sketcher | 2D 约束草图 | ✅ |
| Draft | 2D 绘制和注释 | ✅ |
| Arch | 建筑信息模型 (BIM) | ✅ |
| Mesh | 网格处理 | ✅ |
| Surface | 曲面建模 | ✅ |
| PartDesign | 零件设计 | ✅ |
| TechDraw | 工程图、技术标注 | ✅ |
| Spreadsheet | 电子表格、参数化 | ✅ |
| Assembly | 装配管理 | ✅ |
| Path | CAM 加工路径 | ✅ |
| FEM | 有限元分析 | ✅ |
| Image | 图像处理 | ✅ |
| Material | 材料管理 | ✅ |
| Inspection | 检测和测量 | ✅ |

**图例**: ✅ 已完成 🔄 开发中 📋 计划中

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

LGPL 2.1+

## 联系方式

- GitHub Issues: https://github.com/MiniMax-AI/freecad-cli/issues
