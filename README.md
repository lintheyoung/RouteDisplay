
# 小车轨迹记录可视化上位机
=========
项目使用PyQt构建，用于接收并可视化小车的移动轨迹。

## 使用方法
----

1.  **注意，本项目需要设置波特率为115200。**
2.  在"轨迹保存长度"输入框内，设定希望可视化的轨迹时间长度。
3.  设定坐标轴范围：
    *   X min: X轴的最小范围
    *   X max: X轴的最大范围
    *   Y min: Y轴的最小范围
    *   Y max: Y轴的最大范围
4.  设定参数后，点击“更新画布大小”。你可以自定义背景图片，图片会被自动拉伸到你设定的坐标轴范围尺寸。
5.  你可以直接输入字符串发送到串口。

## 接收与发送格式
-------

本项目使用JSON格式进行串口通信。

*   上位机接收格式如下：

    json

    ```json
    {"x": 0, "y": 124, "head": 0}
    ```

    其中`x`和`y`是小车在2D地图上的世界坐标，`head`是小车的朝向，以Y轴正方向为0度，顺时针角度递增，范围是0~360度。
    发送示例请参考Arduino例程：[SendDemo.ino](https://github.com/lintheyoung/RouteDisplay/blob/main/SendDemo.ino)

*   上位机发送格式如下：

    json

    ```json
    {"text": "start"}
    ```

    接收示例请参考Arduino例程，该实例输入发送"open"点亮D13的LED，"close"熄灭：[RecDemo.ino](https://github.com/lintheyoung/RouteDisplay/blob/main/RecDemo.ino)


## Python文件运行
----------

### 运行环境的设定步骤如下：

1.  克隆项目

    bash

    ```bash
    git clone https://github.com/lintheyoung/RouteDisplay
    ```

2.  安装依赖

    bash

    ```bash
    pip install -r requirements.txt
    ```

3.  运行项目

    bash

    ```bash
    python main.py
    ```


### 文件打包为exe
--------

你可以使用Nuitka打包你的python文件为exe，命令如下：

bash

```bash
nuitka --onefile --windows-icon-from-ico=myapp.ico --windows-disable-console --plugin-enable=pyqt5 main.py
```