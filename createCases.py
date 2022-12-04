# Author: Sun Hao
# Contact: sunhaonuaa@outlook.com
# Copyright (c) 2022 Sun Hao, All rights reserved.

import math
import os
import shutil
import numpy as np

a = 332.5  # 当地声速，m/s
Ma = np.array([0.2, 0.4, 0.6, 0.8])  # 来流马赫数
velocity = Ma * a  # 自由来流速度，m/s
rho = 1.007  # 当地大气密度，kg/m^3
p = 79490  # 当地气压，Pa
nu = (1.7161e-5 * (275.15 / 273.15) ** 1.5 * ((273.15 + 124) / (275.15 + 124))) / rho  # 当地运动粘度，m^2/s
AOA = np.array(
    [-5.0, -4.0, -3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0,
     16.0, 17.0, 18.0, 19.0, 20.0, 21.0, 22.0, 23.0, 24.0, 25.0])  # 计算所用迎角


# 根据关键字修改文件
def updateFile(file, old_str, new_str):
    file_data = ""
    with open(file, "rt") as f:
        for line in f:
            line = line.replace(old_str, new_str)
            file_data += str(line)
    with open(file, "wt") as f:
        f.write(file_data)


if __name__ == '__main__':
    case_dir = "airfoil2D"  # 设置案例目录的名称
    if os.path.exists(case_dir):
        shutil.rmtree(case_dir)  # 如果案例目录已存在，先删除案例目录及里面的内容

    # 生成算例文件
    for i in range(len(Ma)):
        for j in range(len(AOA)):
            shutil.copytree("example", case_dir + "/Ma_" + str(Ma[i]) + "/aoa_" + str(AOA[j]))  # 将示例文件复制到对应目录下
            os.chdir(case_dir + "/Ma_" + str(Ma[i]) + "/aoa_" + str(AOA[j]))

            updateFile("0/p", "internalField_variable", str(p))
            updateFile("0/U", "internalField_variable",
                       "({} {} 0)".format(velocity[i] * math.cos(math.pi / 180 * AOA[j]),
                                          velocity[i] * math.sin(math.pi / 180 * AOA[j])))
            updateFile("constant/transportProperties", "rho_variable", str(rho))
            updateFile("constant/transportProperties", "nu_variable", str(nu))
            updateFile("system/controlDict", "rhoInf_variable", str(rho))
            updateFile("system/controlDict", "magUInf_variable", str(velocity[i]))
            updateFile("system/controlDict", "liftDir_variable", "({} {} 0)".format(-math.sin(math.pi / 180 * AOA[j]),
                                                                                    math.cos(math.pi / 180 * AOA[j])))
            updateFile("system/controlDict", "dragDir_variable", "({} {} 0)".format(math.cos(math.pi / 180 * AOA[j]),
                                                                                    math.sin(math.pi / 180 * AOA[j])))

            os.chdir("../../../")

    # 生成运行脚本
    with open("Allrun.sh", "wt") as run:
        run.write("#!/bin/sh" + '\n')
        for ii in range(len(Ma)):
            for jj in range(len(AOA)):
                run.write("cd " + case_dir + "/Ma_" + str(Ma[ii]) + "/aoa_" + str(AOA[jj]) + '\n')
                run.write("simpleFoam > log &" + '\n')
                run.write("cd ../../../" + '\n')
    run.close()
