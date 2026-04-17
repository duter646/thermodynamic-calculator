# thermodynamic-calculator

热力学与分子运动学 GUI 计算器（中英双语说明）  
Thermodynamics and Molecular Kinetics GUI Calculator (Bilingual README)

---

## 中文说明

### 项目简介

这是一个基于 Python Tkinter 的桌面计算器，用于快速计算理想气体在分子运动论与基础热力学中的常见参数。  
程序支持参数自动推导与单位转换，适合课堂演示、作业验证和工程估算。

### 主要功能

- 状态量求解与互相换算：
	温度 T、压强 p、体积 V、物质的量 n、质量 m、摩尔质量 M。
- 分子运动学参数：
	数密度、平均自由程、最概然速率、平均速率、均方根速率、碰撞频率、平均碰撞时间。
- 热力学相关量：
	平动动能（单分子 / 每摩尔 / 总量）、气体密度、摩尔浓度、分子总数。
- 扩散系数近似：
	使用 $D \approx \frac{1}{3}\lambda \bar{v}$。
- 输入锁定模式：
	勾选“锁定”后，参数作为已知量参与求解；未锁定参数优先作为待求量。
- 内置示例：
	一键加载氮气（室温常压）参数。

### 模型与公式假设

- 理想气体假设。
- 硬球分子模型。
- 主要状态方程：$pV=nRT$。
- 若同时输入多组可互推参数（如 m、n、M），程序会进行一致性检查并给出提示。

### 运行环境

- Python 3.9 或更高版本（推荐 3.10+）
- Tkinter（标准库，通常随 Python 一起安装）
- 无第三方依赖（仅使用 Python 标准库）

### 快速开始

1. 克隆或下载本项目。
2. （可选）创建并激活虚拟环境：

```bash
python -m venv .venv
```

Windows PowerShell:

```bash
.venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
source .venv/bin/activate
```

3. 在项目目录运行：

```bash
python thermodynamics_gui.py
```

4. 在界面中填写已知量，点击“计算”。

### 参数与单位

- 温度：K / C
- 压强：Pa / kPa / MPa / bar / atm
- 体积：m^3 / L / mL
- 质量：kg / g
- 摩尔质量：g/mol（输入），内部自动换算为 kg/mol
- 分子直径：nm（输入），内部自动换算为 m

### 使用建议

- 若只想常规计算：直接填写已知参数，保持全部未锁定。
- 若想强制指定哪些量是“已知”：勾选对应“锁定”。
- 若结果出现“无法计算”：说明当前输入不足以支持该公式，补充相关参数即可。
- 若出现“一致性提示”：表示输入参数之间略有冲突，程序仍会继续计算并提示你复核数据。

### 适用场景

- 物理化学 / 工程热力学教学与学习
- 理想气体近似下的快速估算
- 实验前后参数对照与数量级检查

---

## English

### Overview

This is a Python Tkinter desktop calculator for common quantities in ideal-gas thermodynamics and molecular kinetic theory.  
It supports automatic state-variable derivation and unit conversion, making it useful for class demonstrations, homework checks, and engineering estimation.

### Key Features

- State-variable conversion and solving:
	Temperature T, pressure p, volume V, amount n, mass m, molar mass M.
- Molecular-kinetic quantities:
	Number density, mean free path, most probable speed, mean speed, RMS speed, collision frequency, and mean collision time.
- Thermodynamic quantities:
	Translational kinetic energy (per molecule / per mole / total), gas density, molar concentration, molecule count.
- Diffusion coefficient estimate:
	Uses $D \approx \frac{1}{3}\lambda \bar{v}$.
- Lock mode for inputs:
	Locked fields are treated as known constraints; unlocked fields are solved preferentially.
- Built-in example:
	One-click nitrogen example at room temperature and atmospheric pressure.

### Model Assumptions

- Ideal gas model.
- Hard-sphere molecular model.
- Core equation of state: $pV=nRT$.
- If multiple redundant inputs are provided (for example m, n, M), the app performs consistency checks and shows warnings when needed.

### Requirements

- Python 3.9+ (3.10+ recommended)
- Tkinter (included in standard Python installations in most cases)
- No third-party dependencies (Python standard library only)

### Quick Start

1. Clone or download this repository.
2. (Optional) Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows PowerShell:

```bash
.venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
source .venv/bin/activate
```

3. Run in the project directory:

```bash
python thermodynamics_gui.py
```

4. Fill in known values and click the Calculate button.

### Inputs and Units

- Temperature: K / C
- Pressure: Pa / kPa / MPa / bar / atm
- Volume: m^3 / L / mL
- Mass: kg / g
- Molar mass: g/mol at input, converted internally to kg/mol
- Molecular diameter: nm at input, converted internally to m

### Usage Notes

- For normal usage, enter known values and keep all lock options off.
- Use lock options when you want to explicitly constrain which variables are treated as known.
- If a result says cannot be calculated, more required inputs are needed for that formula.
- If consistency warnings appear, the app still computes outputs but you should recheck the input data.

### Typical Use Cases

- Teaching and learning in physical chemistry and thermodynamics
- Fast estimation under ideal-gas assumptions
- Pre/post experiment parameter sanity checks
