import pygame
import random
import math

# 初始化 pygame
pygame.init()
# 初始化mixer
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=4096)
# 設定全局音量
pygame.mixer.music.set_volume(0.5)  

current_music = None

# 視窗設定
WIDTH, HEIGHT = 768, 640
gameWidth = 448
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("彈幕射擊遊戲")

# 字形
font16 = pygame.font.Font('Asset/fonts/m6x11.ttf', 16)
font32 = pygame.font.Font('Asset/fonts/m6x11.ttf', 32)
font48 = pygame.font.Font('Asset/fonts/m6x11.ttf', 48)

# 方框區域設定
top_left = (gameWidth, 0)
block_size = 32  # 假設每個方塊的大小是 32x32
columns = 10  # 方框的寬度包含 10 個方塊
rows = 20     # 方框的高度包含 20 個方塊

# 加載UI圖片
ui_images = [
    pygame.image.load(f'Asset/BG/UI_{i}.png') for i in range(9)
]
# 加載特效動畫
explosion_images = [
    pygame.image.load(f'Asset/effects/explosion_{i}.png') for i in range(4)
]
isDead_images = [
    pygame.image.load(f'Asset/effects/isDead_{i}.png') for i in range(4)
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
imgEnemyBullet04 = pygame.image.load('Asset/enemy_bullet_4.png')
imgBomb = pygame.image.load('Asset/bomb.png')
imgSmoke = pygame.image.load('Asset/effects/smoke_0.png')
imgBoss = pygame.image.load('Asset/boss.png')

# 預加載BGM
music_tracks = {
    'start': 'Asset/audio/bgm_gamestart.mp3',
    'play': 'Asset/audio/bgm_gameplay.mp3',
    'win': 'Asset/audio/bgm_gamewin.wav',
    'over': 'Asset/audio/bgm_gameover.mp3'
}

# 加載音效
snd_shoot = pygame.mixer.Sound('Asset/audio/snd_shoot.wav')
snd_hit = pygame.mixer.Sound('Asset/audio/snd_hit.wav')
snd_dead = pygame.mixer.Sound('Asset/audio/snd_dead.wav')
snd_alarm = pygame.mixer.Sound('Asset/audio/snd_alarm.MP3')
snd_bomb = pygame.mixer.Sound('Asset/audio/snd_bomb.wav')

# 調整音效音量
snd_hit.set_volume(0.2)
snd_shoot.set_volume(0.2)
snd_alarm.set_volume(0.3)
snd_dead.set_volume(0.2)
snd_bomb.set_volume(0.3)


enemies = []            # 保存敵人
bullets = []            # 保存player子彈
enemy_bullets = []      # 保存敵機子彈
explosions = []         # 保存爆炸特效
bomb_effects = []       # 保存炸彈特效

score = 0 # 分數

# 遊戲狀態
GAME_START = 0
GAME_PLAY = 1
GAME_WIN = 2
GAME_OVER = 3

# Player
playerSize = 32
playerX = gameWidth // 2
playerY = HEIGHT - 50
playerSpeed = 5
playerLives = 3          
isInvincible = False            # 是否處於無敵狀態
invincibleDuration = 2000       # 無敵時間
lastInvincibleTime = 0          # 紀錄開始無敵的時間點
permanentInvincible = False     # 是否使用永久無敵

# 設定射擊間隔和追蹤上次射擊時間
shootCooldown = 200
lastShootTime = 0  # 初始化為0

# 炸彈數量
bomb_count = 3
# 炸彈鍵被按下
bombIsPress = False

# boss死亡
boss_is_defeated = False

# 時鐘
clock = pygame.time.Clock()

# 記錄遊戲開始時間
game_start_time = pygame.time.get_ticks()


# 波次
waves = [
    {
        "time": 1000, # 出現時間(毫秒)
        "enemies": [
            {"type": "Enemy01", "x": gameWidth - 50, "y": 150, "speed": -2, "movement": "straight"},
            {"type": "Enemy01", "x": gameWidth - 150,"y": 150, "speed": -2, "movement": "straight"},
            {"type": "Enemy01", "x": gameWidth - 250,"y": 150, "speed": -2, "movement": "straight"},
            {"type": "Enemy01", "x": 50, "y": 250, "speed": 2, "movement": "straight"},
            {"type": "Enemy01", "x": 150, "y": 250, "speed": 2, "movement": "straight"},
            {"type": "Enemy01", "x": 250, "y": 250, "speed": 2, "movement": "straight"}
        ],
        "triggered": False
    },
    {
        "time": 8000,
        "enemies": [
            {"type": "Enemy02", "x": 50, "y": 75, "speed": 2, "movement": "sine"},
            {"type": "Enemy02", "x": 50,"y": 150, "speed": 2, "movement": "sine"},
            {"type": "Enemy02", "x": 50,"y": 270, "speed": 2, "movement": "sine"},
            {"type": "Enemy02", "x": gameWidth - 50, "y": 75, "speed": -2, "movement": "sine"},
            {"type": "Enemy02", "x": gameWidth - 50,"y": 175, "speed": -2, "movement": "sine"},
            {"type": "Enemy02", "x": gameWidth - 50,"y": 275, "speed": -2, "movement": "sine"}
        ],
        "triggered": False
    },
    {
        "time": 15000,
        "enemies": [
            {"type": "Enemy03", "x": -32, "y": 50, "speed": 2, "movement": "stand", "target_x": 100, "target_y": 50},
            {"type": "Enemy03", "x": -32, "y": 150, "speed": 2, "movement": "stand", "target_x": 100, "target_y": 150},
            {"type": "Enemy03", "x": -32, "y": 250, "speed": 2, "movement": "stand", "target_x": 100, "target_y": 250},
            {"type": "Enemy03", "x": gameWidth + 32, "y": 50, "speed": 2, "movement": "stand", "target_x": gameWidth-100, "target_y": 50},
            {"type": "Enemy03", "x": gameWidth + 32, "y": 150, "speed": 2, "movement": "stand", "target_x": gameWidth-100, "target_y": 150},
            {"type": "Enemy03", "x": gameWidth + 32, "y": 250, "speed": 2, "movement": "stand", "target_x": gameWidth-100, "target_y": 250}
        ],
        "triggered": False
    },
    {
        "time": 30000,
        "enemies": [
            {"type": "Enemy01", "x": -32, "y": 50, "speed": 2, "movement": "waypoint", "waypoints":[(400, 50), (400,600), (50, 600), (50, 50), (500, 50), (500, -500)]},
            {"type": "Enemy01", "x": -132, "y": 50, "speed": 2, "movement": "waypoint", "waypoints":[(400, 50), (400,600), (50, 600), (50, 50), (500, 50), (500, -500)]},
            {"type": "Enemy01", "x": -232, "y": 50, "speed": 2, "movement": "waypoint", "waypoints":[(400, 50), (400,600), (50, 600), (50, 50), (500, 50), (500, -500)]},
            {"type": "Enemy01", "x": -332, "y": 50, "speed": 2, "movement": "waypoint", "waypoints":[(400, 50), (400,600), (50, 600), (50, 50), (500, 50), (500, -500)]},
            {"type": "Enemy01", "x": -432, "y": 50, "speed": 2, "movement": "waypoint", "waypoints":[(400, 50), (400,600), (50, 600), (50, 50), (500, 50), (500, -500)]},
            {"type": "Enemy01", "x": -532, "y": 50, "speed": 2, "movement": "waypoint", "waypoints":[(400, 50), (400,600), (50, 600), (50, 50), (500, 50), (500, -500)]}
        ],
        "triggered": False
    },
    {
        "time": 40000,
        "enemies": [
            {"type": "Enemy01", "x": gameWidth+32, "y": 50, "speed": 2, "movement": "waypoint", "waypoints":[(50, 50), (50,600), (400, 600), (400, 50), (-100, 50), (-100, -500)]},
            {"type": "Enemy01", "x": gameWidth+132, "y": 50, "speed": 2, "movement": "waypoint", "waypoints":[(50, 50), (50,600), (400, 600), (400, 50), (-100, 50), (-100, -500)]},
            {"type": "Enemy01", "x": gameWidth+232, "y": 50, "speed": 2, "movement": "waypoint", "waypoints":[(50, 50), (50,600), (400, 600), (400, 50), (-100, 50), (-100, -500)]},
            {"type": "Enemy01", "x": gameWidth+332, "y": 50, "speed": 2, "movement": "waypoint", "waypoints":[(50, 50), (50,600), (400, 600), (400, 50), (-100, 50), (-100, -500)]},
            {"type": "Enemy01", "x": gameWidth+432, "y": 50, "speed": 2, "movement": "waypoint", "waypoints":[(50, 50), (50,600), (400, 600), (400, 50), (-100, 50), (-100, -500)]},
            {"type": "Enemy01", "x": gameWidth+532, "y": 50, "speed": 2, "movement": "waypoint", "waypoints":[(50, 50), (50,600), (400, 600), (400, 50), (-100, 50), (-100, -500)]}
        ],
        "triggered": False
    },
    # Boss 波次
    {
        "time": 55000,
        "enemies": [
            {
                "type": "Boss",
                "x": gameWidth // 2 - 128,
                "y": -128,
                "speed": 1,
                "movement": "boss"
            }
        ],
        "triggered": False
    }
]

# 繪製初始場景
def draw_start_scene(screen):
    screen.fill((0, 0, 0))
    title_text = font48.render("SHOOTING GAME", True, (255, 255, 255))
    info_text = font32.render("Press any button to start", True, (255, 255, 255))
    screen.blit(title_text, (250, 100))
    screen.blit(info_text, (220, 400))
    # TODO: 裝飾or圖片

# 事件處理(初始)
def handle_start_scene_events(current_state):
    # 取得事件
    for event in pygame.event.get():
        # 離開遊戲
        if event.type == pygame.QUIT:
            return None, False          # (state, running=False)
        # 按下任何鍵開始遊戲
        if event.type == pygame.KEYDOWN:
            # 切到 PLAY 狀態
            return GAME_PLAY, True
    # 如果沒切換場景，就維持當前狀態、running=True
    return current_state, True 

# 繪製勝利場景
def draw_win_scene(screen, final_score):
    # 顯示分數
    screen.fill((0, 0, 0))
    win_text = font48.render("Congratulations!!!", True, (255, 255, 0))
    score_text = font32.render(f"Final Score: {final_score}", True, (255, 255, 255))
    info_text = font32.render("Press any button to restart game", True, (255, 255, 255))
    screen.blit(win_text, (220, 100))
    screen.blit(score_text, (250, 200))
    screen.blit(info_text, (180, 500))
    
# 事件處理(勝利)
def handle_win_scene_events(current_state):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return None, False  # 直接退出
        if event.type == pygame.KEYDOWN:
            # 重新開始遊戲
            reset_game() # 重置遊戲狀態
            return GAME_START, True
    return current_state, True

# 繪製失敗場景
def draw_game_over_scene(screen, final_score):
    screen.fill((0, 0, 0))
    over_text = font48.render("GAME OVER", True, (255, 0, 0))
    score_text = font32.render(f"Final Score: {final_score}", True, (255, 255, 255))
    info_text = font32.render("Press any button to restart game", True, (255, 255, 255))
    screen.blit(over_text, (270, 100))
    screen.blit(score_text, (270, 200))
    screen.blit(info_text, (180, 500))
    # 顯示重新開始或退出提示

# 事件處理(失敗)
def handle_game_over_scene_events(current_state):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return None, False
        if event.type == pygame.KEYDOWN:
            # 重新開始遊戲
            reset_game() # 重置遊戲狀態
            return GAME_START, True
    return current_state, True

# Enemy類
class Enemy:
    def __init__(self, x, y, speed, movement_strategy):
        self.health = 3
        self.img = imgEnemy01
        self.size = 32
        self.x = x
        self.y = y
        self.game_width = gameWidth
        self.game_height = HEIGHT
        self.speed = speed
        self.is_out_of_bound = False
        self.movement_strategy = movement_strategy
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
                explosions.append(
                    Explosion(
                        self.x + self.img.get_width() / 2,
                        self.y + self.img.get_height() / 2,
                        isDead_images
                        )
                    )
    # 發射子彈
    def shoot(self, player_x, player_y):        
        pass
    # 移動或其他通用行為
    def move(self):
        # 呼叫「策略物件」來完成移動邏輯
        self.movement_strategy.move(self)
            
# Enemy01(三方向子彈)
class Enemy01(Enemy):
    def __init__(self, x, y, speed, movement_strategy):
        super().__init__(x, y, speed, movement_strategy)
        self.img = imgEnemy01
        
    def shoot(self, player_x, player_y):
        current_time = pygame.time.get_ticks()
        cooldown = 1500
        # 如果沒設置 last_shoot_time，可以在 __init__ 初始化
        if not hasattr(self, 'last_shoot_time'):
            self.last_shoot_time = 0
        if current_time - self.last_shoot_time > cooldown:
            angle_to_player = math.atan2(player_y - self.y, player_x - self.x) # 計算與player之間的角度
            for i in range(-1, 2):
                bullet_angle = angle_to_player + math.radians(i * 10)
                enemy_bullets.append(EnemyBullet(self.x + self.size / 2, self.y + self.size / 2, bullet_angle))
                self.last_shoot_time = current_time
    
# Enemy02(圓形子彈)
class Enemy02(Enemy):
    def __init__(self, x, y, speed, movement_strategy):
        super().__init__(x, y, speed, movement_strategy)
        self.health = 3
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

# Enemy03() TODO
class Enemy03(Enemy):
    def __init__(self, x, y, speed, movement_strategy):
        super().__init__(x, y, speed, movement_strategy)
        self.health = 5
        self.img = imgEnemy02  #TODO:更換圖片
        self.shoot_cooldown = 100 # 子彈生成冷卻時間
        self.last_shoot_time = 0
        self.time = 0
        self.shoot_angle = 0
        self.shoot_rotation_speed = 20
    
    def shoot(self, player_x, player_y):
        current_time = pygame.time.get_ticks()
        # 射擊邏輯
        center_x = self.x + self.size / 2
        center_y = self.y + self.size / 2
        if current_time - self.last_shoot_time > self.shoot_cooldown:
            self.last_shoot_time = current_time
            # 更新旋轉角度
            self.shoot_angle = (self.shoot_angle + self.shoot_rotation_speed) % 360
            bullet_rad = math.radians(self.shoot_angle)
            enemy_bullets.append(
                EnemyBullet(center_x, center_y, bullet_rad)
            )
           
# Boss
class Boss(Enemy):
    def __init__(self, x, y, speed, movement_strategy):
        super().__init__(x, y, speed, movement_strategy)
        self.health = 100           # Boss 總血量
        self.img = imgBoss          # Boss 圖片
        self.size = 256             # Boss 圖片寬高
        # 旋轉
        self.rotation_angle = 0     # 初始角度
        self.rotation_speed = 2     # 旋轉速度
        # 射擊
        self.shoot_cooldown = 200   # 射擊間隔
        self.last_shoot_time = 0    
        # 二階段標籤
        self.second_phase = False
    
    def shoot(self, player_x, player_y):
        """ 
        Boss 旋轉射擊邏輯：
          - 第一階段：每次發射扇形子彈
          - 第二階段：改用一種瘋狂散射 或 圓形彈
        """
        current_time = pygame.time.get_ticks()
        
        # 如果還沒到目標位置，就不射擊（例如：正在從頂部移動下來）
        if self.speed != 0:
            return
        
        # 根據血量判斷是否啟動第二階段
        if self.health <= 50 and not self.second_phase:
            self.second_phase = True
            print("Boss 進入第二階段！")
        
        if current_time - self.last_shoot_time > self.shoot_cooldown:
            self.last_shoot_time = current_time
            
            if not self.second_phase:
                # === 第一階段：多方向扇形射擊 ===
                center_x = self.x + self.size / 2
                center_y = self.y + self.size / 2
                base_angle = math.radians(self.rotation_angle)  # 跟隨旋轉方向
                
                for i in range(5):
                    angle_i = base_angle + math.radians(i * 72)
                    for j in range(-1, 2):
                        bullet_angle = angle_i + math.radians(j * 5)
                        enemy_bullets.append(
                            EnemyBullet(center_x, center_y, bullet_angle)
                        )       
            else:
                # === 第二階段：圓形彈 or 瘋狂散射 ===
                self.shoot_cooldown = 100
                center_x = self.x + self.size / 2
                center_y = self.y + self.size / 2
                for i in range(8):
                    angle_1 = math.radians(self.rotation_angle + i * 45)
                    enemy_bullets.append(
                        EnemyBulletCircular(center_x, center_y, angle_1)
                    )
    # 複寫isDead()
    def isDead(self):
        global score, boss_is_defeated
        if self.health <= 0:
            if self in enemies:
                enemies.remove(self)
                score += 5000       # Boss 被擊破加更多分
                enemy_bullets.clear()
            for i in range(100):
                explosions.append(
                    Explosion(
                        self.x + self.img.get_width() / 2 + random.randint(-128, 128),
                        self.y + self.img.get_height() / 2 + random.randint(-128, 128),
                        isDead_images
                    )
                )
            boss_is_defeated = True
        
# 移動策略 抽象類 (介面)
class MovementStrategy:
    def move(self, enemy):
        # 子類需實做
        raise NotImplementedError('This method should be overridden by subclass')

# 移動策略 (直線)
class StraightMovement(MovementStrategy):
    def move(self, enemy):
        # 移動邏輯
        enemy.x += enemy.speed
        # 出界檢測與處理
        if enemy.x > enemy.game_width + enemy.size or enemy.x < -enemy.size:
            enemy.speed *= -1  

# 移動策略 (正弦波)
class SineWaveMovement(MovementStrategy):
    def __init__(self):
        self.time = 0
    def move(self, enemy):
        # 移動邏輯
        # 先讓 time 累加。可以把 speed 當做「每幀增加多少時間」
        self.time += 0.5        # 調整數字可改變「走路速度」或「週期」感
        amplitude = 50          # 振幅
        frequency = 0.035       # 頻率
        # 正弦波：x 持續往右，y 隨正弦函式波動
        enemy.x += enemy.speed
        enemy.y += math.sin(self.time * frequency) * amplitude * 0.05
        # 出界檢測與處理
        if (enemy.x > enemy.game_width + 100 or enemy.x < -100 or
            enemy.y > enemy.game_height + 100 or enemy.y < -100):
            enemy.is_out_of_bound = True

# 移動策略(懸停)
class StandMovement(MovementStrategy):
    def __init__(self, target_x, target_y, move_speed = 2):
        super().__init__()
        self.target_x = target_x
        self.target_y = target_y
        self.move_speed = move_speed
        self.reached = False  # 標記是否已經到達目標位置
        
    def move(self, enemy):
        if self.reached:
            return  # 已到達目標位置，不進行移動
        
        # 計算移動方向
        dx = self.target_x - enemy.x
        dy = self.target_y - enemy.y
        distance = math.hypot(dx, dy)
        
        if distance == 0:
            self.reached = True
            enemy.speed = 0  # 停止移動
            return
        
        # 計算單位向量
        dx /= distance
        dy /= distance

        # 移動敵人
        enemy.x += dx * self.move_speed
        enemy.y += dy * self.move_speed
        
        # 檢查是否已經接近目標位置
        if math.hypot(self.target_x - enemy.x, self.target_y - enemy.y) < self.move_speed:
            enemy.x = self.target_x
            enemy.y = self.target_y
            self.reached = True
            enemy.speed = 0  # 停止移動

# 移動策略(路徑點)
class WaypointMovement(MovementStrategy):
    def __init__(self, waypoints, move_speed=2):
        super().__init__()
        self.waypoints = waypoints  # 路點列表，包含 (x, y) 元組
        self.current_waypoint = 0
        self.move_speed = move_speed

    def move(self, enemy):
        if self.current_waypoint >= len(self.waypoints):
            return  # 所有路點已經完成

        target_x, target_y = self.waypoints[self.current_waypoint]

        # 計算移動方向
        dx = target_x - enemy.x
        dy = target_y - enemy.y
        distance = math.hypot(dx, dy)

        if distance == 0:
            self.current_waypoint += 1
            return

        # 計算單位向量
        dx /= distance
        dy /= distance

        # 移動敵人
        enemy.x += dx * self.move_speed
        enemy.y += dy * self.move_speed

        # 檢查是否已經接近當前路點
        if math.hypot(target_x - enemy.x, target_y - enemy.y) < self.move_speed:
            enemy.x = target_x
            enemy.y = target_y
            self.current_waypoint += 1
            
        # 出界檢測(僅上方)
        if (enemy.y < -100):
            enemy.is_out_of_bound = True

# 移動策略(Boss)
class BossMovement(MovementStrategy):
    def __init__(self, target_y = 80):
        super().__init__()
        self.target_y = target_y  # boss目標位置
    def move(self, enemy):
        # 使 boss 下降到指定位置
        if enemy.y < self.target_y:
            enemy.y += enemy.speed
        else:
            enemy.speed = 0
        # 不斷更新角度
        enemy.rotation_angle = (enemy.rotation_angle + enemy.rotation_speed) % 360

# 更新 & 顯示 Enemy
def ShowEnemy():
    global x, y
    for e in enemies:
        # 移動並繪製敵人
        e.move()
        # 呼叫每個敵人的 shoot()
        e.shoot(playerX, playerY)
        
        if hasattr(e, 'rotation_angle'):
            # 以 e.rotation_angle 旋轉
            rotated_image = pygame.transform.rotate(e.img, e.rotation_angle)
            # 修正繪製位置讓 Boss 仍然「置中」
            new_rect = rotated_image.get_rect(center=(e.x + e.size // 2, e.y + e.size // 2))
            screen.blit(rotated_image, new_rect)
        else:
            screen.blit(e.img, (e.x, e.y))

        # 若被標記出界則刪除
        if e.is_out_of_bound and e in enemies:
            enemies.remove(e)

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
                # 添加爆炸特效
                explosions.append(Explosion(
                        bullet_center_x - explosion_images[0].get_width() / 2,
                        bullet_center_y - explosion_images[0].get_height() / 2,
                        explosion_images
                        ))
                # 擊中音效
                snd_hit.play()
                

 #保存現有子彈

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

# 爆炸動畫
class Explosion:
    def __init__(self, x, y, images):
        self.x = x
        self.y = y
        self.images = images                # 一系列爆炸圖片
        self.index = 0                      # 從第 0 幀開始
        self.max_index = len(images) - 1    
        self.frame_duration = 5             # 每張圖片維持幾次主迴圈
        self.frame_count = 0                # 控制換圖速度
        
    # 更新爆炸特效的幀數（換圖邏輯）。
    # 回傳值: 若特效已經播放完畢，則回傳 True 代表可以銷毀
    def update(self):
        self.frame_count += 1
        if self.frame_count >= self.frame_duration:
            self.frame_count = 0
            self.index += 1
            if self.index > self.max_index:
                return True                 # 動畫結束 可銷毀
            return False                    # 動畫尚未結束
    
    # 將爆炸特效繪製到遊戲視窗上
    def draw(self, screen):
        current_image = self.images[self.index]
        screen.blit(current_image, (self.x, self.y))

# 生成敵人
def spawn_enemy(enemy_info):
    # enemy_info: 一個字典，包含 type, x, y, speed, movement 等。
    enemy_type = enemy_info["type"] 
    x = enemy_info["x"]
    y = enemy_info["y"]
    speed = enemy_info["speed"]
    movement_mode = enemy_info.get("movement", "straight")  # 沒定義時預設直線
    
    # 判斷移動策略
    if movement_mode == "sine":
        movement_strategy = SineWaveMovement()
    elif movement_mode == "boss":
        movement_strategy = BossMovement()
    elif movement_mode == "stand":
        target_x = enemy_info.get("target_x", x)
        target_y = enemy_info.get("target_y", y)
        movement_strategy = StandMovement(target_x, target_y, move_speed=3)
    elif movement_mode == "waypoint":
        waypoints = enemy_info.get("waypoints", [])
        movement_strategy = WaypointMovement(waypoints, move_speed=3)
        # ...有其他移動類型也添加在此
    else:
        # 預設用 straight
        movement_strategy = StraightMovement()
    
    
    if enemy_type == "Enemy01":
        return Enemy01(x, y, speed, movement_strategy)
    elif enemy_type == "Enemy02":
        return Enemy02(x, y, speed, movement_strategy)
    elif enemy_type == "Enemy03":
        return Enemy03(x, y, speed, movement_strategy)
    elif enemy_type == "Boss":
        return Boss(x, y, speed, movement_strategy)
    # ...有其他敵人類型也添加在此
    # 預設
    else:
        return Enemy01(x, y, speed, movement_strategy)
        
# 根據波次生成敵人。
def spawn_enemies_by_wave():
    global game_start_time
    # 取得目前遊戲運行時間
    elapsed_time = pygame.time.get_ticks() - game_start_time
    # 檢查波次
    for wave in waves:
        # 如果目前時間已超過 wave["time"] 還未觸發
        if elapsed_time >= wave["time"] and not wave["triggered"]:
            # 生成敵人
            for enemy_info in wave["enemies"]:
                new_enemy = spawn_enemy(enemy_info)
                enemies.append(new_enemy)
                # 檢查是否生成的是 Boss
                if enemy_info["type"] == "Boss":
                    snd_alarm.play()
            # 更改"triggered"標籤，避免重複觸發
            wave["triggered"] = True

# 更新全域管理的子彈
def update_enemy_bullets():
    global isInvincible, playerLives, lastInvincibleTime
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
            if distance(bullet_center_x, bullet_center_y, player_center_x, player_center_y) < 8:
                if not isInvincible:    # 若不在無敵時間
                    playerLives -= 1
                    print(f'玩家受擊，剩{playerLives}次機會')
                    # 受傷音效
                    snd_dead.play()
                    # 進入無敵
                    isInvincible = True
                    lastInvincibleTime = pygame.time.get_ticks()
                    
                    # 檢測是否已死亡
                    if playerLives <= 0:
                        print("GAME OVER!")
                        # TODO: Game Over邏輯
                
                explosions.append(
                    Explosion(
                        bullet_center_x - explosion_images[0].get_width() / 2,
                        bullet_center_y - explosion_images[0].get_height() / 2,
                        isDead_images
                    )
                )
                bullets_to_remove.append(bullet)
    
    for b in bullets_to_remove:
        if b in enemy_bullets:
            enemy_bullets.remove(b)

# 更新並繪製爆炸特效
def update_explosion():
    explosion_to_remove = []
    for exp in explosions:
        # 若收到回傳值 True 則移除特效
        if exp.update():
            explosion_to_remove.append(exp)
        else:
            exp.draw(screen)
    # 移除特效
    for exp in explosion_to_remove:
        if exp in explosions:
            explosions.remove(exp)
    
# 繪製player
def draw_player():
    global isInvincible, permnentInvicible
    #檢查是否過了無敵時間
    if isInvincible:
        current_time = pygame.time.get_ticks()
        if not permanentInvincible:
            if current_time - lastInvincibleTime >= invincibleDuration:
                isInvincible = False
    # 無敵時間 player 閃爍
    if isInvincible:
        # 每0.2秒切換次顯示 or 不顯示
        if((pygame.time.get_ticks() // 200)% 2) == 0:
            screen.blit(imgPlayer, (playerX, playerY)) 
        else:
            pass
    # 非無敵時間正常顯示
    else:
        screen.blit(imgPlayer, (playerX, playerY))
    # 顯示永久無敵狀態
    if permanentInvincible:
        invincible_text = font16.render("Permanent Invincible is ON", True, (255, 0, 0))
        screen.blit(invincible_text, (playerX - 50, playerY + 40))
        
# Player事件處理
def PlayerEvents():
    global playerX, playerY, lastShootTime, bomb_count, bombIsPress  # 宣告全域變數
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
    # 玩家射擊 
    if keys[pygame.K_LSHIFT]:
        currentTime = pygame.time.get_ticks()               # 獲取當前時間
        if currentTime - lastShootTime > shootCooldown:     # 比較時間差
            snd_shoot.play()
            bullets.append(Bullet())
            lastShootTime = currentTime                     # 更新上次射擊時間
    """
    # 使用bomb
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_LCTRL and bomb_count > 0 and not bombIsPress:
            enemy_bullets.clear()                           # 清空敵方子彈
            bomb_count -= 1
            # TODO: 炸彈特效
            # bomb_effects.append((Explosion(playerX, playerY, explosion_images)))  
            bombIsPress = True
            
    # 放開炸彈鍵    
    if event.type == pygame.KEYUP:
        if event.key == pygame.K_LCTRL:
            bombIsPress = False
    """
# 距離判定(歐氏距離)
def distance(x1, y1, x2, y2):
    a = x1 - x2
    b = y1 - y2
    return math.sqrt(a*a + b*b) #開根號

# 顯示分數
def ShowScore(x, y):
    text = f"Score :  {score}"
    score_render = font32.render(text, True, (255, 255, 255))
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
    # 繪製圖片
    screen.blit(imgStar, (top_left[0] + 2*block_size, top_left[1] + 12*block_size))  
    # 繪製分數
    ShowScore(top_left[0] + 2*block_size, top_left[1] + 3*block_size)                
    
    # 繪製殘機
    life_text = font32.render(f'Life : ',True ,(255, 255, 255))
    screen.blit(life_text, (top_left[0] + 2*block_size, top_left[1] + 4.5*block_size))  
    for i in range(playerLives):
        x = top_left[0] + 2*block_size + 70 + i * 48
        y = top_left[1] + 4.5*block_size - 4
        screen.blit(imgPlayer, (x, y))
    
    # 繪製剩餘炸彈
    bomb_text = font32.render(f'Bomb : ',True ,(255, 255, 255))
    screen.blit(bomb_text, (top_left[0] + 2*block_size, top_left[1] + 6*block_size))
    for i in range(bomb_count):
        x = top_left[0] + 2*block_size + 80 + i * 32
        y = top_left[1] + 6*block_size - 4
        screen.blit(imgBomb, (x, y))
        
    # 繪製遊戲時間
    elapsed_ms = pygame.time.get_ticks() - game_start_time  # 經過的毫秒
    elapsed_seconds = elapsed_ms // 1000  # 轉換為秒
    minutes = elapsed_seconds // 60
    seconds = elapsed_seconds % 60
    time_text = f"Time: {minutes:02}:{seconds:02}"  # 格式化為 MM:SS
    time_render = font32.render(time_text, True, (255, 255, 255))
    screen.blit(time_render, (top_left[0] + 2*block_size, top_left[1] + 8.5*block_size))

# 初始化所有變數與物件
def reset_game():
    global enemies, bullets, enemy_bullets, explosions, bomb_effects
    global score, playerX, playerY, playerLives
    global isInvincible, invincibleDuration, lastInvincibleTime
    global shootCooldown, lastShootTime
    global bomb_count, bombIsPress
    global boss_is_defeated
    global waves
    global game_start_time
    global permanentInvincible

    # 清空所有列表
    enemies.clear()
    bullets.clear()
    enemy_bullets.clear()
    explosions.clear()
    bomb_effects.clear()

    # 重置分數
    score = 0

    # 重置玩家位置和狀態
    playerX = gameWidth // 2
    playerY = HEIGHT - 50
    playerLives = 3
    isInvincible = False
    lastInvincibleTime = 0
    permanentInvincible = False

    # 重置射擊相關變數
    shootCooldown = 200
    lastShootTime = 0

    # 重置炸彈數量和狀態
    bomb_count = 3
    bombIsPress = False

    # 重置 Boss 狀態
    boss_is_defeated = False

    # 重置波次觸發狀態
    for wave in waves:
        wave["triggered"] = False
    
    # 重置遊戲開始時間    
    game_start_time = pygame.time.get_ticks()

# 切換音樂
def play_music_preloaded(state):
    global current_music
    music_path = music_tracks.get(state)
    if music_path and current_music != music_path:
        pygame.mixer.music.stop()
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.play(-1)
        current_music = music_path

# 遊戲主迴圈
running = True
current_state = GAME_START
final_score = 0
reset_game()

while running:
    # 初始場景
    if current_state == GAME_START:
        # 繪製場景
        draw_start_scene(screen)
        pygame.display.update()
        # BGM
        play_music_preloaded('start')
        # 事件處理
        current_state, running = handle_start_scene_events(current_state)
    # 遊戲主體        
    elif current_state == GAME_PLAY:
        # 取得事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # 處理一次性的按鍵按下/放開
            if event.type == pygame.KEYDOWN:
                # 使用炸彈
                if event.key == pygame.K_LCTRL and bomb_count > 0 and not bombIsPress:
                    enemy_bullets.clear()
                    bomb_count -= 1
                    bombIsPress = True
                    snd_bomb.play()
                # 處理 RCTRL 鍵以啟用永久無敵
                if event.key == pygame.K_RETURN:
                    isInvincible = True
                    permanentInvincible = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LCTRL:
                    bombIsPress = False
        # 填充背景顏色
        screen.blit(imgBackGround, (0,0))
        play_music_preloaded('play')
        # 更新並繪製遊戲元素
        draw_player()
        ShowEnemy()  
        update_enemy_bullets()
        update_explosion()  
        PlayerEvents()
        showBullets()
        spawn_enemies_by_wave()
        DrawUI()
        pygame.display.update()  # 更新顯示
        clock.tick(60)  # 控制遊戲速度
        # 檢測勝負
        if boss_is_defeated:
            final_score = score
            current_state = GAME_WIN
        if playerLives <= 0:
            final_score = score
            current_state = GAME_OVER
    # 勝利場景
    elif current_state == GAME_WIN:
        draw_win_scene(screen, final_score)
        pygame.display.update()
        play_music_preloaded('win')
        current_state, running = handle_win_scene_events(current_state)
    # 失敗場景
    elif current_state == GAME_OVER:
        draw_game_over_scene(screen, final_score)
        pygame.display.update()
        play_music_preloaded('over')
        current_state, running = handle_game_over_scene_events(current_state)
 
pygame.mixer.music.stop()   
pygame.quit()