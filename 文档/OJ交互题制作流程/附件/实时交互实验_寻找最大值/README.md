# 寻找最大值：北航 OJ 实时交互实验

本项目通过 SPJ 重新调用北航 OJ 的运行监控器，实现选手程序与交互控制器之间的实时双向问答。已在实验题 10296 上完成真实 OJ 验证：C 提交 [8185647](https://accoding.buaa.edu.cn:4000/submission/8185647)、C++ 提交 [8185648](https://accoding.buaa.edu.cn:4000/submission/8185648) 均为 36/36 组 AC。错误答案、询问超限、未刷新输出、答对后异常退出四种反例均为 WA。

## 使用哪些文件

- `problem.md`：包含本平台预运行规则的题面草案。
- `answer.c`：可直接提交的 C 标程，兼容预运行和正式交互。
- `compare_interactive.cpp`：后台 SPJ 代码框应粘贴的完整 C++14 源码。
- `data/`：正式 OJ 数据；每个 `.in` 都只有 `0`，对应 `.ans` 保存 `n` 和隐藏排列。共 36 组。
- `local_data/`、`run_local.py`：普通本地双向管道练习环境。
- `generate_data.py`：同时重建本地数据和 OJ 数据，同步 SPJ 打包副本。
- `verify.py`：标程、交互协议、样例和小排列核验。
- `test_native_adapter.py`：一次性 Linux 容器内的通信层测试；使用运行器替身，不能代替真实 OJ 验证。
- `negative_submissions/`：用于验证判题的错误提交。
- `接入实验记录.md`、`oj_experiments.json`：平台试验的证据与进展。

后台入口：[实验题 10296](https://accoding.buaa.edu.cn:4000/problem/10296/index)。本项目仍是实验实现，不自动加入课程比赛。

## 实际运行过程

1. OJ 按正常流程编译并启动选手程序，输入 `0`。选手程序立即正常退出。
2. OJ 调用 SPJ。SPJ 从 `.ans` 读取隐藏排列，只向选手发送公开信息。
3. SPJ 在 `/test` 下创建独立的临时通信目录，通过 `/utils/process_monitor` 再次启动当前提交 `/test/main`。选手仍以 uid/gid 8194 运行，设定 1000 ms、65536 KB、最多 5 个进程。
4. 监控器将选手的标准输入输出接到两条 FIFO。SPJ 发出真实的 `n`，读到 `? l r` 后立即计算并发送回复；之后的询问由选手根据回复决定。
5. SPJ 检查询问格式、区间、次数、最终答案，以及监控器的运行结果和退出码。正常完成才返回 `1`；错误、超时、缺失最终答案或异常退出返回 `0`。

隐藏数据所在目录不向选手开放。选手不能直接访问通信目录；FIFO 由监控器在降低身份前打开，选手只使用标准输入输出。提交程序不会直接以 SPJ 的 root 身份执行。没有修改 OJ 的后台脚本、运行器或权限配置。

## 后台配置

在编辑题目的高级设置中启用 SPJ，粘贴 `compare_interactive.cpp`。当前后台实际使用 C++14 编译 SPJ；语言选 C++。本版本只支持编译为 `/test/main` 的 C/C++ 提交。

将 `data/` 中同名的 `.in` 与 `.ans` 成对添加为测试点。不要把 `.ans` 的隐藏排列放入选手输入。若替换已有测试点且文件名改变，应删除旧测试点并新增；本次实测发现，仅上传不同名字的替换文件不会更新原有测试点的引用。

基本设置中的单组时间填 **500 ms**，内存填 **65536 KB**。这只限制预运行；正式交互仍由 SPJ 内部设置为每组 1000 ms。当前后台要求外层总时间不超过 30000 ms，36 组若填写 1000 ms 会被拒绝，填写 500 ms 后合计 18000 ms。

`data/makefile` 和 `data/compare.cpp` 也构成符合旧文档的源码包，执行 `make` 会生成 `compare`。但本次后台实测直接编译 SPJ 代码框，上传文件在 `/data/data/`；不能靠上传这个 makefile 自动启动交互服务。实际接入使用上面的 SPJ 代码框。

## 本地运行

在本目录运行：

    python3 generate_data.py
    python3 run_local.py --case 03 --log demo_transcript.txt
    python3 verify.py

运行自己的已编译程序：

    python3 run_local.py --case 03 -- /absolute/path/to/program

Linux 通信层测试需在一次性容器内执行；脚本会创建 `/test` 和 `/utils/process_monitor` 替身，不能在真实评测机或常用系统上直接运行：

    docker run --rm --network none -v "$PWD:/work:ro" ai-dl-tauri-ubuntu-arm64:22.04 python3 /work/test_native_adapter.py

这是本机已有的测试镜像名称；其他环境可使用含 Python 3、GCC/G++ 的 Linux 镜像。

## 实验限制

本实现依赖当前评测镜像的 `/test/main`、`/utils/process_monitor`、命令行参数、身份编号及 SPJ 能够再次启动监控器。这些是实测的内部接口，不是稳定的官方交互 API。更换评测镜像后需要重新验证；缺少运行器时判题不会退化为以 root 直接执行提交。

页面的耗时、内存统计来自预运行，不能用于比较真实算法耗时；正式交互由内层运行监控器单独执行资源限制。SPJ 另设 3 秒墙钟等待和错误后的清理等待，避免因未刷新输出而一直等待。

默认第二行只输出 `Accepted` 或 `Wrong Answer`，使当前后台正确显示 AC/WA。调试编译时加 `-DSPJ_DIAGNOSTIC` 可输出详细原因，但本次后台可能将带附加文字的失败结果显示为 Other Error，得分仍为 0。

算法改编自 [CF 1486C1](https://codeforces.com/contest/1486/problem/C1)，原站评分为 1600。题解中的 Accoding 难度栏保留待评；后台实验题的临时难度字段不作为算法评级。课程是否已讲授二分尚未确认，因此当前交付为交互实验草案。
