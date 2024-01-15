import numpy as np

# 读取包含复数的文件
complex_path = 'fly-float-100k.dat'
complex_data = np.fromfile(complex_path, dtype=np.complex64)

# 分离实部和虚部
real_part = np.real(complex_data)
imaginary_part = np.imag(complex_data)

# 将实部和虚部分别存储到两个文件中
real_path = 'real_part.dat'
imag_path = 'imaginary_part.dat'

real_part.tofile(real_path)
imaginary_part.tofile(imag_path)
