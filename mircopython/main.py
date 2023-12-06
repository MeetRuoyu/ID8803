from machine import Pin, I2C, UART
import imu
import utime
import time

# WiFi路由器信息，请填上自己的WiFi路由器信息
SSID = 'LAPTOP-9R8DR218'  # 替换为您的WiFi名称
password = '010217111'  # 替换为您的WiFi密码
remote_IP = '192.168.137.1'  # 替换为您的电脑IP地址
remote_Port = '8080'  # 远程端口号
local_Port = '1112'  # 本地端口号

# 串口映射到GP0和GP1端口上
esp_uart = UART(0, baudrate=115200, tx=Pin(0), rx=Pin(1))

# 初始化MPU6050
i2c_1 = I2C(0, sda=Pin(16), scl=Pin(17), freq=400000)
mpu1 = imu.MPU6050(i2c_1)
i2c_2 = I2C(1, sda=Pin(14), scl=Pin(15), freq=400000)
mpu2 = imu.MPU6050(i2c_2)

# 发送AT命令的函数
def esp_sendCMD(cmd, ack, timeout=5000):
    esp_uart.write(cmd + '\r\n')
    start_time = utime.ticks_ms()
    while utime.ticks_diff(utime.ticks_ms(), start_time) < timeout:
        if esp_uart.any():
            response = esp_uart.read().decode()
            print(response)
            if ack in response:
                return True
    return False

# 配置和连接WiFi
esp_sendCMD("AT+CWJAP=\"{}\",\"{}\"".format(SSID, password), "OK", 20000)

# 设置UDP连接
esp_sendCMD("AT+CIPSTART=\"UDP\",\"{}\",{},{}".format(remote_IP, remote_Port, local_Port), "OK", 10000)

# 开启透传模式
esp_sendCMD("AT+CIPMODE=1", "OK")

# 准备发送数据
esp_sendCMD("AT+CIPSEND", ">")

# 主循环
while True:
    # 从MPU6050读取数据
    accel1, gyro1, temp1 = mpu1.accel.xyz, mpu1.gyro.xyz, mpu1.temperature
    accel2, gyro2, temp2 = mpu2.accel.xyz, mpu2.gyro.xyz, mpu2.temperature

    # 创建要发送的消息
    message = "MPU1 Accel: {}, Gyro: {}, Temp: {}; MPU2 Accel: {}, Gyro: {}, Temp: {}\r\n".format(accel1, gyro1, temp1, accel2, gyro2, temp2)
    
    # 发送数据
    esp_uart.write(message)
    print("Data sent: " + message)

    # 等待响应或新数据
    utime.sleep(1)

    # 检查是否收到了数据
    if esp_uart.any():
        response = esp_uart.read().decode()
        print("Received: " + response)
