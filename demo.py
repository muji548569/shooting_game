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

# 分數
score = 0
font = pygame.font.Font('Asset/fonts/m6x11.ttf', 32)

# 時鐘
clock = pygame.time.Clock()

# 方框區域設定
top_left = (gameWidth, 0)
block_size = 32  # 假設每個方塊的大小是 32x32
columns = 10  # 方框的寬度包含 10 個方塊
rows = 20     # 方框的高度包含 20 個方塊

# 加載UI圖片
ui_images = [
    pygame.image.load(f'Asset/BG/UI_{i}.png') for i in range(9)
]
# 加載圖片
imgBackGround = pygame.image.load('Asset/BG/space.png')
imgStar = pygame.image.load('Asset/Star.png')
imgPlayer = pygame.image.load('Asset/player.png')
imgLauncher = pygame.image.load('Asset/launcher.png')
imgPlayerBullet01 = pygame.image.load('Asset/player_bullet_1.png')
imgEnemy01 = pygame.image.load('Asset/enemy_01.png')
imgEnemy02 = pygame.image.load('Asset/enemy_02.png')
imgEnemyBullet01 = pygame.image.load('Asset/enemy_bullet_1.png')
imgEnemyBullet02 = pygame.image.load('Asset/enemy_bullet_2.png')
imgEnemyBullet03 = pygame.image.load('Asset/enemy_bullet_3.png')

# 添加音效 todo

# Player
playerSize = 32
playerX = gameWidth // 2
playerY = HEIGHT - 50
playerSpeed = 5

# Enemy類
class Enemy():
    def __init__(self, x, y, speed):
        self.health = 3
        self.img = imgEnemy01
        self.size = 32
        self.x = x
        self.y = y
        self.speed = speed
    # 受擊
    def Hurt(self):
        self.health -= 1
    # 死亡
    def isDead(self):
        global score
        for e in enemies:
            if(self.health <= 0):
                if self in enemies:
                    enemies.remove(self)
                    score += 500
    # 發射子彈
    def shoot(self, player_x, player_y):
        
        pass
    # 移動或其他通用行為
    def move(self):
        """
        移動或其他通用行為，可在這裡處理。
        """
        self.x += self.speed
        # 出界判斷
        if self.x > gameWidth + 2*self.size or self.x < -2*self.size:
            self.speed *= -1

# Enemy01(三方向)
class Enemy01(Enemy):
    def __init__(self, x, y, speed):
        super().__init__(x, y, speed)
        self.img = imgEnemy01
        
    def shoot(self, player_x, player_y):
        current_time = pygame.time.get_ticks()
        cooldown = 1000
        # 如果沒設置 last_shoot_time，可以在 __init__ 初始化
        if not hasattr(self, 'last_shoot_time'):
            self.last_shoot_time = 0
        if current_time - self.last_shoot_time > cooldown:
            angle_to_player = math.atan2(player_y - self.y, player_x - self.x) # 計算與player之間的角度
            for i in range(-1, 2):
                bullet_angle = angle_to_player + math.radians(i * 10)
                enemy_bullets.append(EnemyBullet(self.x + self.size / 2, self.y + self.size / 2, bullet_angle))
                self.last_shoot_time = current_time
    def move(self):
        """
        先呼叫父類別的 move()，再加上其它特殊邏輯 (如果有需要)。
        """
        super().move()
            
# Enemy02(圓形)
class Enemy02(Enemy):
    def __init__(self, x, y, speed):
        super().__init__(x, y, speed)
        self.img = imgEnemy02
        self.shoot_cooldown = 1000 # 子彈生成冷卻時間
        self.last_shoot_time = 0

    def shoot(self, player_x, player_y):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shoot_time > self.shoot_cooldown:
            radius = 15  # 子彈初始圓形排列的半徑
            for i in range(8):  # 生成圓形排列的8個子彈
                angle = math.radians(i * 45)  # 每個子彈相隔45度
                initial_x = self.x + self.size / 2 + radius * math.cos(angle) #計算初始位置
                initial_y = self.y + self.size / 2 + radius * math.sin(angle)
                enemy_bullets.append(
                    EnemyBulletCircular(initial_x, initial_y, angle)
                )
            self.last_shoot_time = current_time
              
    def move(self):
        """
        先呼叫父類別的 move()，再加上其它特殊邏輯 (如果有需要)。
        """
        super().move()

# 生成Enemy
def ShowEnemy():
    global x, y
    for e in enemies:
        # 移動並繪製敵人
        e.move()
        screen.blit(e.img, (e.x, e.y))
        # 呼叫每個敵人的 shoot()
        e.shoot(playerX, playerY)

    
# Bullet類
class Bullet():
    def __init__(self):
        self.img = imgPlayerBullet01
        self.x = playerX + 8
        self.y = playerY - 10
        self.speed = 10
    #碰撞檢測
    def Collision(self):
        global score
        for e in enemies:
            bullet_center_x = self.x + self.img.get_width() / 2
            bullet_center_y = self.y + self.img.get_height() / 2
            enemy_center_x = e.x + e.size / 2
            enemy_center_y = e.y + e.size / 2
            if distance(bullet_center_x, bullet_center_y, enemy_center_x, enemy_center_y) < 20:
                if self in bullets:  # 確保子彈仍然存在於列表中
                    bullets.remove(self)
                e.Hurt()  # 減少敵人生命值
                e.isDead()  # 刪除敵人
                score += 100
                print(score)

 #保存現有子彈
bullets = [] # 保存player子彈

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

# Enemy Bullet 類
class EnemyBullet:
    def __init__(self, x, y, angle):
        self.img = imgEnemyBullet02
        self.x = x
        self.y = y
        self.speed = 2
        self.angle = angle  # 移動角度

    def move(self):
        self.x += self.speed * math.cos(self.angle)
        self.y += self.speed * math.sin(self.angle)

    def draw(self, screen):
        screen.blit(self.img, (self.x, self.y))

    def is_off_screen(self):
        return self.x < 0 or self.x > gameWidth or self.y < 0 or self.y > HEIGHT

# 敵人圓形子彈類
class EnemyBulletCircular:
    def __init__(self, x, y, angle):
        self.img = imgEnemyBullet02
        self.x = x
        self.y = y
        self.speed = 2
        self.angle = angle  # 移動角度
        
    def move(self):
        self.x += self.speed * math.cos(self.angle)
        self.y += self.speed * math.sin(self.angle)

    def draw(self, screen):
        screen.blit(self.img, (self.x, self.y))

    def is_off_screen(self):
        return (self.x < 0 or self.x > gameWidth or 
                self.y < 0 or self.y > HEIGHT)
        

# todo 敵人出現時間軸
numbersOfEnemies = 3
enemies = []
for i in range(numbersOfEnemies):
    enemies.append(Enemy01(random.randint(100, 300), 100, 2))
    enemies.append(Enemy02(150, random.randint(100, 300), 1))  

# 保存敵機子彈
enemy_bullets = []

# 2. 更新全域管理的子彈
def update_enemy_bullets():
    bullets_to_remove = []
    for bullet in enemy_bullets:
        bullet.move()
        bullet.draw(screen)
        if bullet.is_off_screen():
            bullets_to_remove.append(bullet)
        else:
            # 偵測與玩家碰撞
            bullet_center_x = bullet.x + bullet.img.get_width() / 2
            bullet_center_y = bullet.y + bullet.img.get_height() / 2
            player_center_x = playerX + playerSize / 2
            player_center_y = playerY + playerSize / 2
            if distance(bullet_center_x, bullet_center_y, player_center_x, player_center_y) < 10:
                """
                todo 玩家受傷邏輯
                """
                print('玩家受傷')
                bullets_to_remove.append(bullet)
    
    for b in bullets_to_remove:
        if b in enemy_bullets:
            enemy_bullets.remove(b)


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

# 顯示分數
def ShowScore(x, y):
    text = f"Score :  {score}"
    score_render = font.render(text, True, (255, 255, 255))
    screen.blit(score_render, (x, y))

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
    screen.blit(imgStar, (top_left[0] + 2*block_size, top_left[1] + 12*block_size))
    ShowScore(top_left[0] + 2*block_size, top_left[1] + 3*block_size)

# 遊戲主迴圈
running = True

while running:
    # 填充背景顏色
    screen.blit(imgBackGround, (0,0))   
    
    # 處理事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    #玩家圖像
    screen.blit(imgPlayer, (playerX, playerY))
    ShowEnemy()  
    update_enemy_bullets()  
    PlayerEvents()
    showBullets()
    
    
    DrawUI()
    pygame.display.update()  # 更新顯示
    clock.tick(60)  # 控制遊戲速度
    
pygame.quit()