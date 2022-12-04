# Author: Sun Hao
# Contact: sunhaonuaa@outlook.com
# Copyright (c) 2022 Sun Hao, All rights reserved.

import os
from itertools import islice
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from geomdl import fitting

Ma = np.array([0.2, 0.4, 0.6, 0.8])  # 来流马赫数
AOA = np.array(
    [-5.0, -4.0, -3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0,
     16.0, 17.0, 18.0])  # 计算需用迎角


def draw_residuals(y1, y2, y3, x):
    config = {
        "mathtext.fontset": 'stix',  # matplotlib渲染数学字体时使用的字体，和Times New Roman差别不大
        "font.family": 'serif',  # 衬线字体
        "font.size": 12,  # 定义字号
        "font.serif": ['SimSun'],  # 自制的TimesSong字体，该字体英文为新罗马，中文为宋体
        'axes.unicode_minus': False  # 处理负号，即-号
    }
    plt.rcParams['xtick.direction'] = 'in'  # 将x轴的刻度线方向设置向内
    plt.rcParams['ytick.direction'] = 'in'  # 将y轴的刻度线方向设置向内
    rcParams.update(config)
    # print(matplotlib.matplotlib_fname())    # 定位同目录下的fonts文件夹，便于安装字体
    # print(matplotlib.get_cachedir())    # 字体缓存目录

    x = np.array(x)
    y1 = np.array(y1)
    y2 = np.array(y2)
    y3 = np.array(y3)

    y = [y1, y2, y3]
    y_label = ["$\mathrm{p}$", "$\mathrm{U_x}$", "$\mathrm{U_y}$"]

    plt.ion()  # 打开交互模式
    for yi in range(len(y)):
        plt.plot(x, y[yi], label=y_label[yi])
        plt.xscale('log')

    plt.xlabel("Time(s)")
    plt.ylabel("Residuals")
    # plt.title('Residuals')
    plt.legend(loc="upper right", fontsize=12, frameon=False)
    # 保存图片至本地
    plt.savefig(os.path.join('residual.svg'), transparent=True)
    # plt.show()
    plt.close()


def draw_forcecoeffs(x, y, x_label, y_label, path):
    config = {
        "mathtext.fontset": 'stix',  # matplotlib渲染数学字体时使用的字体，和Times New Roman差别不大
        "font.family": 'serif',  # 衬线字体
        "font.size": 12,  # 定义字号
        "font.serif": ['SimSun'],  # 自制的TimesSong字体，该字体英文为新罗马，中文为宋体
        'axes.unicode_minus': False  # 处理负号，即-号
    }
    plt.rcParams['xtick.direction'] = 'in'  # 将x轴的刻度线方向设置向内
    plt.rcParams['ytick.direction'] = 'in'  # 将y轴的刻度线方向设置向内
    rcParams.update(config)
    plt.ion()  # 打开交互模式

    points = []
    # 绘制曲线
    for ii in range(len(x)):
        point = [x[ii], y[ii]]
        points.append(point)
        if ii % len(AOA) == len(AOA) - 1:
            degree = 2  # 插值曲线次数
            # 曲线插值
            curve = fitting.interpolate_curve(points, degree)
            evalpts = np.array(curve.evalpts)

            plt.plot(evalpts[:, 0], evalpts[:, 1], label="Ma="+str(Ma[int((ii+1) / len(AOA) - 1)]))
            # 绘制数值点
            # pts = np.array(points)
            # plt.scatter(pts[:, 0], pts[:, 1], color="red")
            points = []
        ii += 1

    plt.xlabel(x_label)
    plt.ylabel(y_label)
    # plt.title('Force Coeffs')
    plt.legend(loc="best", fontsize=12, frameon=False)
    # 保存图片至本地
    plt.savefig(path, transparent=True)
    # plt.show()
    plt.close()


if __name__ == '__main__':
    case_dir = "airfoil2D"  # 设置案例目录的名称
    CM, CD, CL = [], [], []

    for i in range(len(Ma)):
        for j in range(len(AOA)):
            os.chdir(case_dir + "/Ma_" + str(Ma[i]) + "/aoa_" + str(AOA[j]))

            # 绘制残差图
            ux, uy, p, time = [], [], [], []
            with open('postProcessing/residuals/0/residuals.dat') as f:
                for line in islice(f, 3, None):
                    time.append(float((line.split()[0])))
                    p.append(float((line.split()[1])))
                    ux.append(float((line.split()[2])))
                    uy.append(float((line.split()[3])))
            f.close()
            draw_residuals(p, ux, uy, time)

            # 绘制升力/迎角曲线、阻力/迎角曲线、力矩/迎角曲线、升力/阻力曲线(极曲线)。
            cm, cd, cl = [], [], []
            with open('postProcessing/forceCoeffs_object/0/forceCoeffs.dat') as f:
                for line in islice(f, 9 + 700 * 2, None):  # 700秒后的数据参与计算
                    cm.append(float((line.split()[1])))
                    cd.append(float((line.split()[2])))
                    cl.append(float((line.split()[3])))
                CM.append(sum(cm) / len(cm))
                CD.append(sum(cd) / len(cd))
                CL.append(sum(cl) / len(cl))
            f.close()
            os.chdir("../../../")
    draw_forcecoeffs(np.tile(AOA, len(Ma)), CL, "Angle of Attack ($\mathrm{°}$)", "$\mathrm{C_L}$",
                       "pics/CL_AOA.svg")
    draw_forcecoeffs(np.tile(AOA, len(Ma)), CD, "Angle of Attack ($\mathrm{°}$)", "$\mathrm{C_D}$",
                       "pics/CD_AOA.svg")
    draw_forcecoeffs(np.tile(AOA, len(Ma)), CM, "Angle of Attack ($\mathrm{°}$)", "$\mathrm{C_M}$",
                       "pics/CM_AOA.svg")
    draw_forcecoeffs(CD, CL, "$\mathrm{C_D}$", "$\mathrm{C_L}$", "pics/CL_CD.svg")
