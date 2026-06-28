# Debug / Verify / Validate 脚本整理说明

目录约定：

- `scripts/debug/`：临时诊断、一次性排查、数据库/时间戳探查
- `scripts/verify/`：验证/核对类脚本（通常生成报告或做交叉比对）
- `scripts/validate/`：校验类脚本（通常检查数据完整性、时间覆盖、格式正确性）

说明：
- `scripts/verify_n_structure.py` 仍然是规范入口，保持不动。
- 根目录历史脚本 `verify_n_structure.py` / `verify_matrix_consistency.py` 已迁移到 `scripts/verify/` 下的 `*_root.py` 归档版本。
- 后续新脚本请按职责归类，避免再次堆回根目录或 scripts/ 顶层。
