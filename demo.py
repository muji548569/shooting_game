import pygame
import random
import math

# 初始化 pygame
pygame.init()

# 視窗設定
WIDTH, HEIGHT = 768, 640
gameWidth = 448
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("彈幕射擊遊戲")

# 加載UI圖片
ui_images = [
    pygame.image.load(f'Asset/BG/UI_{i}.png') for i in range(9)
]

# 加載圖片
imgStar = pygame.image.load('Asset/Star.png')
imgPlayer = pygame.image.load('Asset/player.png')
imgLauncher = pygame.image.load('Asset/launcher.png')
imgPlayerBullet01 = pygame.image.load('Asset/player_bullet_1.png')
imgEnemy01 = pygame.image.load('Asset/enemy_01.png')
imgEnemyBullet01 = pygame.image.load('Asset/enemy_bullet_1.png')



# 方框區域設定
top_left = (gameWidth, 0)
block_size = 32  # 假設每個方塊的大小是 32x32
columns = 10  # 方框的寬度包含 10 個方塊
rows = 20     # 方框的高度包含 20 個方塊

# Player
playerSize = 32
playerX = gameWidth // 2
playerY = HEIGHT - 50
playerSpeed = 5

# Enemy類
class Enemy():
    def __init__(self, img, x, y, speed):
        self.health = 3
        self.img = img
        self.size = 32
        self.x = x
        self.y = y
        self.speed = speed
    # 受擊
    def Hurt(self):
        self.health -= 1
    

numbersOfEnemies = 5
enemies = []
for i in range(numbersOfEnemies):
    enemies.append(Enemy(imgEnemy01, random.randint(100, 300), 100, 2))

# 生成Enemy
def ShowEnemy():
    global x, y, speed
    for e in enemies:
        screen.blit(e.img, (e.x, e.y))
        e.x += e.speed
        # 出界判斷
        if e.x > gameWidth + 2*e.size or e.x < 0 - 2*e.size:
            e.speed *= -1
            # todo 刪除自身
    
# Bullet類
class Bullet():
    def __init__(self):
        self.img = imgPlayerBullet01
        self.x = playerX + 8
        self.y = playerY - 10
        self.speed = 10
    #碰撞檢測
    def Collision(self):
        for e in enemies:
            if(distance(self.x, self.y, e.x, e.y) < 15):
                if self in bullets:  # 確保子彈仍然存在於列表中
                    bullets.remove(self)
                e.Hurt()  # 減少敵人生命值

 #保存現有子彈
bullets = []

# 生成子彈
def showBullets():
    bullets_to_remove = []  # 暫存需要移除的子彈
    for b in bullets:
        screen.blit(b.img, (b.x, b.y))
        b.Collision()  # 碰撞檢測
        b.y -= b.speed
        if b.y < -30:
            bullets_to_remove.append(b)
    # 移除需要刪除的子彈
    for bullet in bullets_to_remove:
        if bullet in bullets:  # 確保子彈仍然存在於列表中
            bullets.remove(bullet)


# 設定射擊間隔和追蹤上次射擊時間
shootCooldown = 200
lastShootTime = 0  # 初始化為0

# Player事件處理
def PlayerEvents():
    global playerX, playerY, lastShootTime  # 宣告全域變數
    # 玩家移動
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and playerX > 0:
        playerX -= playerSpeed
    if keys[pygame.K_RIGHT] and playerX < gameWidth - playerSize:
        playerX += playerSpeed
    if keys[pygame.K_UP] and playerY > 0:
        playerY -= playerSpeed
    if keys[pygame.K_DOWN] and playerY < HEIGHT - playerSize:
        playerY += playerSpeed
    #玩家射擊
    if keys[pygame.K_LSHIFT]:
        currentTime = pygame.time.get_ticks()   # 獲取當前時間
        if currentTime - lastShootTime > shootCooldown:  # 比較時間差
            bullets.append(Bullet())
            lastShootTime = currentTime  # 更新上次射擊時間

# 距離判定(歐氏距離)
def distance(x1, y1, x2, y2):
    a = x1 - x2
    b = y1 - y2
    return math.sqrt(a*a + b*b) #開根號

# 繪製右側UI框
def DrawUI():
    # 繪製方框
    for row in range(rows):
        for col in range(columns):
            # 判斷是否在方框的邊緣
            if row == 0 and col == 0:
                image = ui_images[0]  # 左上角
            elif row == 0 and col == columns - 1:
                image = ui_images[2]  # 右上角
            elif row == rows - 1 and col == 0:
                image = ui_images[6]  # 左下角
            elif row == rows - 1 and col == columns - 1:
                image = ui_images[8]  # 右下角
            elif row == 0:
                image = ui_images[1]  # 上邊
            elif row == rows - 1:
                image = ui_images[7]  # 下邊
            elif col == 0:
                image = ui_images[3]  # 左邊
            elif col == columns - 1:
                image = ui_images[5]  # 右邊
            else:
                image = ui_images[4]  # 中間
            
            # 計算位置並繪製圖片
            x = top_left[0] + col * block_size
            y = top_left[1] + row * block_size
            screen.blit(image, (x, y))
    screen.blit(imgStar, (512, 400))

# 時鐘
clock = pygame.time.Clock()

# 遊戲主迴圈
running = True

# 初始化enemy
enemy01 = Enemy(imgEnemy01, gameWidth/2, 100, 5)

while running:
    # 填充背景顏色
    screen.fill((0, 0, 0))   
    
    # 處理事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    #玩家圖像
    screen.blit(imgPlayer, (playerX, playerY))
    PlayerEvents()
    ShowEnemy()
    showBullets()
    
    DrawUI()
    
    # 更新顯示
    pygame.display.update()
    
    # 控制遊戲速度
    clock.tick(60)
