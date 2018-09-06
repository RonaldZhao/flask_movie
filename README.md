# Flask 构建微电影视频网站

学习慕课网课程 [Python Flask 构建微电影视频网站](https://coding.imooc.com/class/124.html) 的代码.

## 开发环境

1. OS: windows10 pro
2. Python: 3.6.6
3. 虚拟化环境: virtualenv
4. 代码编辑器: Atom

## 创建虚拟化环境

> 注意: 在进行此步骤之前请确保`python`已安装.

首先安装`virtualenv`: `pip install virtualenv`.

然后`cd`到你要把虚拟环境保存的目录, 然后执行`virtualenv movie --no-site-packages`.

最后执行`.\movie\Scripts\activate`激活虚拟环境.(如果是PowerShell的话请参考[Windows PowerShell 无法激活 python 虚拟环境问题的解决](https://ronaldzhao.top/devtools/powershell.html))

> 退出虚拟环境命令: `.\movie\Scripts\deactivate.bat`

## 安装 Flask

请先执行`pip freeze`确保没有输出, 即环境干净, 如果有输出请检查是否是在创建虚拟环境的时候没有使用`--no-site-packages`参数.(虚拟环境的删除只要把该目录删除即可)

然后执行`pip install flask`安装 Flask.

安装完毕后再次执行`pip freeze`可以看到:

```bash
(movie) λ pip freeze
click==6.7
Flask==1.0.2
itsdangerous==0.24
Jinja2==2.10
MarkupSafe==1.0
Werkzeug==0.14.1
(movie) λ
```
