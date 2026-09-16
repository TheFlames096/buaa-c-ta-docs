# 程设助教文档互助

面向北航程序设计基础课程的助教与同学，集中整理环境配置、代码风格和编译纠错文档，欢迎共同补充与勘误。

所有教学文档统一放在 **`文档/`** 下，每份文档独占一个子文件夹，同时提供 **Markdown 在线阅读版与 PDF 下载版**。配图和必要附件跟随对应文档存放，方便单独取用。

## 文档索引

| 文档 | 在线阅读 | PDF | 内容 |
| --- | --- | --- | --- |
| VS Code C 语言环境配置 · Windows | [Markdown](文档/VSCode配置-Windows/VS_Code_C语言环境配置指南.md) | [PDF](文档/VSCode配置-Windows/VS_Code_C语言环境配置指南.pdf) | MinGW-w64 GCC、GDB、编译运行与断点调试 |
| VS Code C 语言环境配置 · macOS | [Markdown](文档/VSCode配置-macOS/VS_Code_C语言环境配置指南_macOS.md) | [PDF](文档/VSCode配置-macOS/VS_Code_C语言环境配置指南_macOS.pdf) | Apple Clang、LLDB、编译运行与断点调试 |
| 码道 IDE C 语言环境配置 · HarmonyOS | [Markdown](文档/码道IDE配置-HarmonyOS/码道IDE_C语言环境配置指南_HarmonyOS.md) | [PDF](文档/码道IDE配置-HarmonyOS/码道IDE_C语言环境配置指南_HarmonyOS.pdf) | 码道 IDE、Harmonybrew、Clang 与终端输入输出 |
| C 语言代码风格与编译纠错 | [Markdown](文档/C语言代码风格与编译纠错/C语言代码风格与编译纠错指南.md) | [PDF](文档/C语言代码风格与编译纠错/C语言代码风格与编译纠错指南.pdf) | 缩进命名、编译诊断、常见语法和逻辑错误 |

环境配置文档按自己的操作系统选读。HarmonyOS 指南保留原文的验证范围说明，目前尚未在 MateBook Fold 实机完成全流程测试。

## 如何使用

- 在线阅读：点击上表中的 Markdown，可直接查看正文和配图。
- 下载 PDF：点击 PDF 后使用 GitHub 文件页的下载按钮。
- 下载全部：在仓库首页选择 **Code → Download ZIP**，解压后按文档目录阅读。
- 使用示例工程：Windows 和 macOS 文档均附带 `.vscode` 配置与 `C1/A.c`。下载完整仓库后，在 VS Code 中打开下面对应的工程文件夹；也可以将该文件夹整体复制为自己的课程工作区。

| 系统 | 打开的工程文件夹 |
| --- | --- |
| Windows | [文档/VSCode配置-Windows/附件/windows](文档/VSCode配置-Windows/附件/windows) |
| macOS | [文档/VSCode配置-macOS/附件/macOS](文档/VSCode配置-macOS/附件/macOS) |

示例配置与 Markdown 第 6 节保持一致。Windows 的编译器路径需要按实际安装位置修改；编译器和 VS Code 扩展请按指南自行安装。macOS 教程中“解压双系统包”的操作，在本仓库对应打开上表的 `macOS` 工程目录。

## 目录约定

```text
buaa-c-ta-docs/
├── README.md
├── .gitignore
└── 文档/
    ├── VSCode配置-Windows/
    │   ├── VS_Code_C语言环境配置指南.md
    │   ├── VS_Code_C语言环境配置指南.pdf
    │   └── 附件/windows/          # .vscode 配置与 C1/A.c
    ├── VSCode配置-macOS/
    │   ├── VS_Code_C语言环境配置指南_macOS.md
    │   ├── VS_Code_C语言环境配置指南_macOS.pdf
    │   └── 附件/macOS/            # .vscode 配置与 C1/A.c
    ├── 码道IDE配置-HarmonyOS/
    │   ├── 码道IDE_C语言环境配置指南_HarmonyOS.md
    │   └── 码道IDE_C语言环境配置指南_HarmonyOS.pdf
    └── C语言代码风格与编译纠错/
        ├── C语言代码风格与编译纠错指南.md
        ├── C语言代码风格与编译纠错指南.pdf
        └── 配图/
```

## 一起完善

发现错误、步骤失效或希望新增内容，请在 [Issues](https://github.com/y38501148-max/buaa-c-ta-docs/issues) 留言，写清文档名称、章节或 PDF 页码、问题现象及建议。环境问题请附系统、编译器版本和可复制的报错文字。

提交修改时：

1. Fork 仓库，修改对应文档，然后提交 Pull Request。
2. 新文档放入 `文档/文档名称/`，提供同名 `.md` 与 `.pdf`，并补充首页索引。
3. 修改正文时同步更新 PDF，检查代码块、分页、图片和链接。只修改配套工程时，核对它与正文中的配置是否一致。
4. 图片使用相对路径，放在该文档的 `配图/`；其他必要文件放在 `附件/`。保留引用来源及适用版本说明。
5. 提交自己有权公开的资料；示例和截图去除个人联系方式、登录凭据、学生名册等信息，课程群二维码和未公开试题不放入仓库。

首批文档整理于 2026-09-16，来自现有课程资料成品；正文与 PDF 保留原版，码风 PDF 仅统一了文件名。后续软件界面和配置变化，欢迎提交实测勘误。
