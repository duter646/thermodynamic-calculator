"""热力学 GUI 计算器。

功能：
- 平均自由程
- 最概然速率 / 平均速率 / 均方根速率
- 数密度
- 碰撞频率与平均碰撞时间
- 平动动能（单分子、每摩尔、总量）
- 气体密度
- 扩散系数近似
- 质量、体积、压强、物质的量之间的相互换算

假设：
- 理想气体
- 硬球分子模型
"""

from __future__ import annotations

import math
import tkinter as tk
from tkinter import messagebox, ttk
from tkinter.scrolledtext import ScrolledText

# Physical constants (SI)
K_B = 1.380649e-23  # Boltzmann constant, J/K
N_A = 6.02214076e23  # Avogadro constant, 1/mol
R = 8.314462618  # Gas constant, J/(mol*K)

PRESSURE_UNITS = {
    "Pa": 1.0,
    "kPa": 1.0e3,
    "MPa": 1.0e6,
    "bar": 1.0e5,
    "atm": 101325.0,
}

TEMP_UNITS = ("K", "C")
VOLUME_UNITS = {
    "m^3": 1.0,
    "L": 1.0e-3,
    "mL": 1.0e-6,
}
MASS_UNITS = {
    "kg": 1.0,
    "g": 1.0e-3,
}


def fmt(value: float, unit: str, digits: int = 6) -> str:
    """Format numbers for readable output."""
    if value == 0:
        return f"0 {unit}".strip()
    abs_value = abs(value)
    if abs_value >= 1e4 or abs_value < 1e-3:
        number = f"{value:.{digits}e}"
    else:
        number = f"{value:.{digits}f}".rstrip("0").rstrip(".")
    return f"{number} {unit}".strip()


def entry_fmt(value: float) -> str:
    """Format values for entry boxes with compact significant digits."""
    return f"{value:.10g}"


class ThermodynamicsApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("热力学参数计算器")
        self.root.geometry("920x660")
        self.root.minsize(860, 600)

        self._build_ui()

    def _build_ui(self) -> None:
        container = ttk.Frame(self.root, padding=12)
        container.pack(fill=tk.BOTH, expand=True)

        container.columnconfigure(0, weight=1)
        container.columnconfigure(1, weight=1)
        container.rowconfigure(1, weight=1)

        title = ttk.Label(
            container,
            text="热力学与分子运动参数计算器",
            font=("Segoe UI", 13, "bold"),
        )
        title.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

        input_frame = ttk.LabelFrame(container, text="输入参数", padding=12)
        input_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 8))
        input_frame.columnconfigure(1, weight=1)
        input_frame.columnconfigure(3, weight=0)

        result_frame = ttk.LabelFrame(container, text="计算结果", padding=12)
        result_frame.grid(row=1, column=1, sticky="nsew", padx=(8, 0))
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)

        self.result_box = ScrolledText(
            result_frame,
            wrap=tk.WORD,
            height=24,
            font=("Consolas", 10),
            state=tk.DISABLED,
        )
        self.result_box.grid(row=0, column=0, sticky="nsew")

        # 输入参数（允许留空，程序会尝试自动推导）
        self.temp_var = tk.StringVar(value="300")
        self.temp_unit_var = tk.StringVar(value="K")
        self.pressure_var = tk.StringVar(value="101325")
        self.pressure_unit_var = tk.StringVar(value="Pa")
        self.molar_mass_var = tk.StringVar(value="28.97")
        self.diameter_var = tk.StringVar(value="0.37")
        self.moles_var = tk.StringVar(value="1.0")
        self.volume_var = tk.StringVar(value="")
        self.volume_unit_var = tk.StringVar(value="L")
        self.mass_var = tk.StringVar(value="")
        self.mass_unit_var = tk.StringVar(value="g")

        # 锁定状态：锁定后该参数作为已知量参与求解，未锁定则视为待求量。
        self.lock_temp_var = tk.BooleanVar(value=False)
        self.lock_pressure_var = tk.BooleanVar(value=False)
        self.lock_molar_mass_var = tk.BooleanVar(value=False)
        self.lock_diameter_var = tk.BooleanVar(value=False)
        self.lock_moles_var = tk.BooleanVar(value=False)
        self.lock_volume_var = tk.BooleanVar(value=False)
        self.lock_mass_var = tk.BooleanVar(value=False)

        row = 0
        self._add_entry(input_frame, row, "温度", self.temp_var, "T", self.lock_temp_var)
        ttk.Combobox(
            input_frame,
            textvariable=self.temp_unit_var,
            values=TEMP_UNITS,
            width=8,
            state="readonly",
        ).grid(row=row, column=2, sticky="w", padx=(6, 0), pady=4)

        row += 1
        self._add_entry(input_frame, row, "压强", self.pressure_var, "p", self.lock_pressure_var)
        ttk.Combobox(
            input_frame,
            textvariable=self.pressure_unit_var,
            values=list(PRESSURE_UNITS.keys()),
            width=8,
            state="readonly",
        ).grid(row=row, column=2, sticky="w", padx=(6, 0), pady=4)

        row += 1
        self._add_entry(
            input_frame, row, "摩尔质量 (g/mol)", self.molar_mass_var, "M", self.lock_molar_mass_var
        )

        row += 1
        self._add_entry(input_frame, row, "分子直径 (nm)", self.diameter_var, "d", self.lock_diameter_var)

        row += 1
        self._add_entry(input_frame, row, "物质的量 (mol)", self.moles_var, "n", self.lock_moles_var)

        row += 1
        self._add_entry(input_frame, row, "体积", self.volume_var, "V", self.lock_volume_var)
        ttk.Combobox(
            input_frame,
            textvariable=self.volume_unit_var,
            values=list(VOLUME_UNITS.keys()),
            width=8,
            state="readonly",
        ).grid(row=row, column=2, sticky="w", padx=(6, 0), pady=4)

        row += 1
        self._add_entry(input_frame, row, "质量", self.mass_var, "m_total", self.lock_mass_var)
        ttk.Combobox(
            input_frame,
            textvariable=self.mass_unit_var,
            values=list(MASS_UNITS.keys()),
            width=8,
            state="readonly",
        ).grid(row=row, column=2, sticky="w", padx=(6, 0), pady=4)

        row += 1
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=row, column=0, columnspan=4, sticky="ew", pady=(10, 4))
        button_frame.columnconfigure((0, 1, 2), weight=1)

        ttk.Button(button_frame, text="计算", command=self.calculate).grid(
            row=0, column=0, sticky="ew", padx=3
        )
        ttk.Button(button_frame, text="示例：氮气", command=self.load_example).grid(
            row=0, column=1, sticky="ew", padx=3
        )
        ttk.Button(button_frame, text="清空", command=self.clear_results).grid(
            row=0, column=2, sticky="ew", padx=3
        )

        formula_text = (
            "模型假设：理想气体 + 硬球分子\n"
            "勾选“锁定”表示该参数为已知量；未锁定参数将优先作为待求量\n"

        )
        ttk.Label(input_frame, text=formula_text, justify=tk.LEFT).grid(
            row=row + 1, column=0, columnspan=4, sticky="w", pady=(10, 0)
        )

    def _add_entry(
        self,
        parent: ttk.Frame,
        row: int,
        label: str,
        var: tk.StringVar,
        symbol: str,
        lock_var: tk.BooleanVar,
    ) -> None:
        ttk.Label(parent, text=f"{label} ({symbol})").grid(row=row, column=0, sticky="w", pady=4)
        ttk.Entry(parent, textvariable=var, width=20).grid(
            row=row, column=1, sticky="ew", padx=(8, 0), pady=4
        )
        ttk.Checkbutton(parent, text="锁定", variable=lock_var).grid(
            row=row, column=3, sticky="w", padx=(8, 0), pady=4
        )

    @staticmethod
    def _parse_optional_float(raw_text: str, field_name: str) -> float | None:
        text = raw_text.strip()
        if not text:
            return None
        try:
            return float(text)
        except ValueError as exc:
            raise ValueError(f"{field_name} 请输入有效的数字。") from exc

    @staticmethod
    def _state_line(label: str, value: float | None, unit: str, source: str | None) -> str:
        if value is None:
            return f"{label:<24}: 未提供/无法推导"
        suffix = f"（{source}）" if source else ""
        return f"{label:<24}: {fmt(value, unit)}{suffix}"

    @staticmethod
    def _result_line(label: str, value: float | None, unit: str, requirement: str) -> str:
        if value is None:
            return f"{label:<24}: 无法计算（需 {requirement}）"
        return f"{label:<24}: {fmt(value, unit)}"

    def _get_inputs(self) -> dict[str, object]:
        temp_raw = self._parse_optional_float(self.temp_var.get(), "温度")
        pressure_raw = self._parse_optional_float(self.pressure_var.get(), "压强")
        volume_raw = self._parse_optional_float(self.volume_var.get(), "体积")
        moles_raw = self._parse_optional_float(self.moles_var.get(), "物质的量")
        mass_raw = self._parse_optional_float(self.mass_var.get(), "质量")
        molar_mass_raw = self._parse_optional_float(self.molar_mass_var.get(), "摩尔质量")
        diameter_raw = self._parse_optional_float(self.diameter_var.get(), "分子直径")

        locked = {
            "T": self.lock_temp_var.get(),
            "p": self.lock_pressure_var.get(),
            "V": self.lock_volume_var.get(),
            "n_mol": self.lock_moles_var.get(),
            "mass_kg": self.lock_mass_var.get(),
            "M": self.lock_molar_mass_var.get(),
            "d": self.lock_diameter_var.get(),
        }
        has_any_lock = any(locked.values())

        if has_any_lock:
            if locked["T"] and temp_raw is None:
                raise ValueError("温度已锁定，请输入数值。")
            if locked["p"] and pressure_raw is None:
                raise ValueError("压强已锁定，请输入数值。")
            if locked["V"] and volume_raw is None:
                raise ValueError("体积已锁定，请输入数值。")
            if locked["n_mol"] and moles_raw is None:
                raise ValueError("物质的量已锁定，请输入数值。")
            if locked["mass_kg"] and mass_raw is None:
                raise ValueError("质量已锁定，请输入数值。")
            if locked["M"] and molar_mass_raw is None:
                raise ValueError("摩尔质量已锁定，请输入数值。")
            if locked["d"] and diameter_raw is None:
                raise ValueError("分子直径已锁定，请输入数值。")

        use_temp_raw = temp_raw if (locked["T"] or not has_any_lock) else None
        use_pressure_raw = pressure_raw if (locked["p"] or not has_any_lock) else None
        use_volume_raw = volume_raw if (locked["V"] or not has_any_lock) else None
        use_moles_raw = moles_raw if (locked["n_mol"] or not has_any_lock) else None
        use_mass_raw = mass_raw if (locked["mass_kg"] or not has_any_lock) else None
        use_molar_mass_raw = molar_mass_raw if (locked["M"] or not has_any_lock) else None
        use_diameter_raw = diameter_raw if (locked["d"] or not has_any_lock) else None

        temperature_k = None
        if use_temp_raw is not None:
            if self.temp_unit_var.get() == "C":
                temperature_k = use_temp_raw + 273.15
            else:
                temperature_k = use_temp_raw
            if temperature_k <= 0:
                raise ValueError("温度必须大于 0 K。")

        pressure_pa = None
        if use_pressure_raw is not None:
            pressure_pa = use_pressure_raw * PRESSURE_UNITS[self.pressure_unit_var.get()]
            if pressure_pa <= 0:
                raise ValueError("压强必须大于 0 Pa。")

        volume_m3 = None
        if use_volume_raw is not None:
            volume_m3 = use_volume_raw * VOLUME_UNITS[self.volume_unit_var.get()]
            if volume_m3 <= 0:
                raise ValueError("体积必须为正数。")

        moles = None
        if use_moles_raw is not None:
            if use_moles_raw <= 0:
                raise ValueError("物质的量必须为正数。")
            moles = use_moles_raw

        mass_kg = None
        if use_mass_raw is not None:
            mass_kg = use_mass_raw * MASS_UNITS[self.mass_unit_var.get()]
            if mass_kg <= 0:
                raise ValueError("质量必须为正数。")

        molar_mass_kg_per_mol = None
        if use_molar_mass_raw is not None:
            if use_molar_mass_raw <= 0:
                raise ValueError("摩尔质量必须为正数。")
            molar_mass_kg_per_mol = use_molar_mass_raw / 1000.0

        diameter_m = None
        if use_diameter_raw is not None:
            if use_diameter_raw <= 0:
                raise ValueError("分子直径必须为正数。")
            diameter_m = use_diameter_raw * 1.0e-9

        provided = {
            "T": temperature_k is not None,
            "p": pressure_pa is not None,
            "V": volume_m3 is not None,
            "n_mol": moles is not None,
            "mass_kg": mass_kg is not None,
            "M": molar_mass_kg_per_mol is not None,
            "d": diameter_m is not None,
        }

        if not any(provided.values()):
            raise ValueError("请至少输入一个参数。")

        return {
            "T": temperature_k,
            "p": pressure_pa,
            "V": volume_m3,
            "n_mol": moles,
            "mass_kg": mass_kg,
            "M": molar_mass_kg_per_mol,
            "d": diameter_m,
            "provided": provided,
            "locked": locked,
            "lock_mode": has_any_lock,
        }

    def _fill_derived_entries(self, state: dict[str, float | None], provided: dict[str, bool]) -> None:
        """Write derived values back to empty entry boxes for quick parameter conversion."""
        T = state["T"]
        p = state["p"]
        V = state["V"]
        n_mol = state["n_mol"]
        mass_kg = state["mass_kg"]
        M = state["M"]

        if (not provided["T"]) and T is not None:
            if self.temp_unit_var.get() == "C":
                self.temp_var.set(entry_fmt(T - 273.15))
            else:
                self.temp_var.set(entry_fmt(T))

        if (not provided["p"]) and p is not None:
            factor = PRESSURE_UNITS[self.pressure_unit_var.get()]
            self.pressure_var.set(entry_fmt(p / factor))

        if (not provided["V"]) and V is not None:
            factor = VOLUME_UNITS[self.volume_unit_var.get()]
            self.volume_var.set(entry_fmt(V / factor))

        if (not provided["n_mol"]) and n_mol is not None:
            self.moles_var.set(entry_fmt(n_mol))

        if (not provided["mass_kg"]) and mass_kg is not None:
            factor = MASS_UNITS[self.mass_unit_var.get()]
            self.mass_var.set(entry_fmt(mass_kg / factor))

        if (not provided["M"]) and M is not None:
            self.molar_mass_var.set(entry_fmt(M * 1000.0))

    def _derive_state(self, state: dict[str, float | None]) -> tuple[dict[str, float | None], list[str]]:
        T = state["T"]
        p = state["p"]
        V = state["V"]
        n_mol = state["n_mol"]
        mass_kg = state["mass_kg"]
        M = state["M"]

        warnings: list[str] = []

        if M is not None and mass_kg is not None and n_mol is not None:
            n_from_mass = mass_kg / M
            rel = abs(n_from_mass - n_mol) / max(abs(n_mol), 1.0e-12)
            if rel > 1.0e-3:
                warnings.append("输入的质量、物质的量和摩尔质量不完全一致，已按已输入值继续计算。")

        changed = True
        while changed:
            changed = False

            if M is None and mass_kg is not None and n_mol is not None:
                M = mass_kg / n_mol
                changed = True

            if n_mol is None and mass_kg is not None and M is not None:
                n_mol = mass_kg / M
                changed = True

            if mass_kg is None and n_mol is not None and M is not None:
                mass_kg = n_mol * M
                changed = True

            # Ideal-gas state conversion: solve one unknown from the other three.
            if T is None and p is not None and V is not None and n_mol is not None:
                T = p * V / (n_mol * R)
                changed = True

            if p is None and n_mol is not None and T is not None and V is not None:
                p = n_mol * R * T / V
                changed = True

            if V is None and n_mol is not None and T is not None and p is not None:
                V = n_mol * R * T / p
                changed = True

            if n_mol is None and p is not None and V is not None and T is not None:
                n_mol = p * V / (R * T)
                changed = True

        if T is not None and T <= 0:
            raise ValueError("由输入参数推导出的温度不合理（<= 0 K），请检查输入。")

        if p is not None and p <= 0:
            raise ValueError("由输入参数推导出的压强不合理（<= 0 Pa），请检查输入。")

        if V is not None and V <= 0:
            raise ValueError("由输入参数推导出的体积不合理（<= 0 m^3），请检查输入。")

        if n_mol is not None and n_mol <= 0:
            raise ValueError("由输入参数推导出的物质的量不合理（<= 0 mol），请检查输入。")

        if M is not None and M <= 0:
            raise ValueError("由输入参数推导出的摩尔质量不合理（<= 0 kg/mol），请检查输入。")

        if mass_kg is not None and mass_kg <= 0:
            raise ValueError("由输入参数推导出的质量不合理（<= 0 kg），请检查输入。")

        return {
            "T": T,
            "p": p,
            "V": V,
            "n_mol": n_mol,
            "mass_kg": mass_kg,
            "M": M,
            "d": state["d"],
        }, warnings

    def calculate(self) -> None:
        try:
            data = self._get_inputs()
            provided = data["provided"]
            locked = data["locked"]
            lock_mode = data["lock_mode"]
            state, warnings = self._derive_state(
                {
                    "T": data["T"],
                    "p": data["p"],
                    "V": data["V"],
                    "n_mol": data["n_mol"],
                    "mass_kg": data["mass_kg"],
                    "M": data["M"],
                    "d": data["d"],
                }
            )
        except ValueError as err:
            messagebox.showerror("输入错误", str(err))
            return

        self._fill_derived_entries(state, provided)

        T = state["T"]
        p = state["p"]
        V = state["V"]
        n_mol = state["n_mol"]
        mass_kg = state["mass_kg"]
        M = state["M"]
        d = state["d"]

        molecular_mass = (M / N_A) if M is not None else None

        number_density_pt = (p / (K_B * T)) if (p is not None and T is not None) else None
        number_density_nv = (n_mol * N_A / V) if (n_mol is not None and V is not None) else None
        number_density = number_density_pt if number_density_pt is not None else number_density_nv
        if number_density_pt is not None and number_density_nv is not None:
            rel = abs(number_density_pt - number_density_nv) / max(abs(number_density_pt), 1.0e-12)
            if rel > 1.0e-3:
                warnings.append("由 p/T 与 n/V 计算得到的数密度存在差异。")

        mean_free_path = None
        if number_density is not None and d is not None:
            mean_free_path = 1.0 / (math.sqrt(2.0) * math.pi * d * d * number_density)

        v_most_probable = None
        v_mean = None
        v_rms = None
        if T is not None and molecular_mass is not None:
            v_most_probable = math.sqrt(2.0 * K_B * T / molecular_mass)
            v_mean = math.sqrt(8.0 * K_B * T / (math.pi * molecular_mass))
            v_rms = math.sqrt(3.0 * K_B * T / molecular_mass)

        collision_frequency = None
        mean_collision_time = None
        if v_mean is not None and mean_free_path is not None:
            collision_frequency = v_mean / mean_free_path
            mean_collision_time = mean_free_path / v_mean

        kinetic_energy_per_molecule = (1.5 * K_B * T) if T is not None else None
        kinetic_energy_per_mole = (1.5 * R * T) if T is not None else None
        translational_internal_energy = None
        if n_mol is not None and kinetic_energy_per_mole is not None:
            translational_internal_energy = n_mol * kinetic_energy_per_mole
        elif p is not None and V is not None:
            translational_internal_energy = 1.5 * p * V

        gas_density_ideal = None
        if p is not None and M is not None and T is not None:
            gas_density_ideal = p * M / (R * T)

        gas_density_mass_volume = None
        if mass_kg is not None and V is not None:
            gas_density_mass_volume = mass_kg / V

        if gas_density_ideal is not None and gas_density_mass_volume is not None:
            rel = abs(gas_density_ideal - gas_density_mass_volume) / max(abs(gas_density_ideal), 1.0e-12)
            if rel > 1.0e-3:
                warnings.append("由状态方程计算的气体密度与质量/体积计算值存在差异。")

        gas_density_nmv = None
        if n_mol is not None and M is not None and V is not None:
            gas_density_nmv = n_mol * M / V

        gas_density = gas_density_ideal
        if gas_density is None:
            gas_density = gas_density_mass_volume
        if gas_density is None:
            gas_density = gas_density_nmv
        diffusion_coefficient = (
            (1.0 / 3.0) * mean_free_path * v_mean
            if (mean_free_path is not None and v_mean is not None)
            else None
        )
        molecule_count = (n_mol * N_A) if n_mol is not None else None
        molar_concentration = (n_mol / V) if (n_mol is not None and V is not None) else None

        source_t = "输入" if provided["T"] else ("推导" if T is not None else None)
        source_p = "输入" if provided["p"] else ("推导" if p is not None else None)
        source_v = "输入" if provided["V"] else ("推导" if V is not None else None)
        source_n = "输入" if provided["n_mol"] else ("推导" if n_mol is not None else None)
        source_mass = "输入" if provided["mass_kg"] else ("推导" if mass_kg is not None else None)
        source_m = "输入" if provided["M"] else ("推导" if M is not None else None)
        source_d = "输入" if provided["d"] else None

        if lock_mode:
            lock_tips = []
            if locked["T"]:
                lock_tips.append("T")
            if locked["p"]:
                lock_tips.append("p")
            if locked["V"]:
                lock_tips.append("V")
            if locked["n_mol"]:
                lock_tips.append("n")
            if locked["mass_kg"]:
                lock_tips.append("m_total")
            if locked["M"]:
                lock_tips.append("M")
            if locked["d"]:
                lock_tips.append("d")
            output_mode_line = f"锁定模式：已启用（已锁定: {', '.join(lock_tips) if lock_tips else '无'}）"
        else:
            output_mode_line = "锁定模式：未启用（按已填写参数自动求解）"

        output = [
            output_mode_line,
            "",
            "=== 状态量（SI）与来源 ===",
            self._state_line("温度 T", T, "K", source_t),
            self._state_line("压强 p", p, "Pa", source_p),
            self._state_line("体积 V", V, "m^3", source_v),
            self._state_line("物质的量 n", n_mol, "mol", source_n),
            self._state_line("质量 m_total", mass_kg, "kg", source_mass),
            self._state_line("摩尔质量 M", M, "kg/mol", source_m),
            self._state_line("分子质量 m", molecular_mass, "kg", None),
            self._state_line("分子直径 d", d, "m", source_d),
            "",
            "=== 分子运动论结果 ===",
            self._result_line("数密度 N/V", number_density, "1/m^3", "(T, p) 或 (n, V)"),
            self._result_line("平均自由程 lambda", mean_free_path, "m", "d + 数密度"),
            self._result_line("最概然速率 v_mp", v_most_probable, "m/s", "T, M"),
            self._result_line("平均速率 v_avg", v_mean, "m/s", "T, M"),
            self._result_line("均方根速率 v_rms", v_rms, "m/s", "T, M"),
            self._result_line("碰撞频率 z", collision_frequency, "1/s", "lambda, v_avg"),
            self._result_line("平均碰撞时间 tau", mean_collision_time, "s", "lambda, v_avg"),
            self._result_line("扩散系数 D（近似）", diffusion_coefficient, "m^2/s", "lambda, v_avg"),
            "",
            "=== 热力学相关量 ===",
            self._result_line("气体密度 rho", gas_density, "kg/m^3", "(质量,体积) 或 (n,M,V) 或 (p,M,T)"),
            self._result_line("摩尔浓度 c=n/V", molar_concentration, "mol/m^3", "n, V"),
            self._result_line("单分子平均平动动能", kinetic_energy_per_molecule, "J", "T"),
            self._result_line("每摩尔平均平动动能", kinetic_energy_per_mole, "J/mol", "T"),
            self._result_line("总平动内能 U", translational_internal_energy, "J", "(n,T) 或 (p,V)"),
            self._result_line("分子总数 N", molecule_count, "", "n"),
        ]

        if warnings:
            output.extend(["", "=== 提示 ==="])
            for warning in warnings:
                output.append(f"- {warning}")

        self.result_box.config(state=tk.NORMAL)
        self.result_box.delete("1.0", tk.END)
        self.result_box.insert(tk.END, "\n".join(output))
        self.result_box.config(state=tk.DISABLED)

    def clear_results(self) -> None:
        self.result_box.config(state=tk.NORMAL)
        self.result_box.delete("1.0", tk.END)
        self.result_box.config(state=tk.DISABLED)

    def load_example(self) -> None:
        # 氮气室温常压示例参数
        self.temp_var.set("300")
        self.temp_unit_var.set("K")
        self.pressure_var.set("101325")
        self.pressure_unit_var.set("Pa")
        self.molar_mass_var.set("28.0134")
        self.diameter_var.set("0.364")
        self.moles_var.set("1.0")
        self.volume_var.set("")
        self.volume_unit_var.set("L")
        self.mass_var.set("")
        self.mass_unit_var.set("g")

        self.lock_temp_var.set(False)
        self.lock_pressure_var.set(False)
        self.lock_molar_mass_var.set(False)
        self.lock_diameter_var.set(False)
        self.lock_moles_var.set(False)
        self.lock_volume_var.set(False)
        self.lock_mass_var.set(False)


def main() -> None:
    root = tk.Tk()
    app = ThermodynamicsApp(root)
    app.calculate()
    root.mainloop()


if __name__ == "__main__":
    main()
