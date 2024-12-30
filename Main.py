import pygame
import random
import math

# 初始化 pygame
pygame.init()

# 視窗設定
WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("彈幕射擊遊戲")

# 顏色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# 玩家設定
player_size = 20
player_x = WIDTH // 2
player_y = HEIGHT - 50
player_speed = 5

# 玩家子彈
player_bullets = []
player_bullet_speed = -10

# 敵人
enemies = []
enemy_size = 30

# 敵人子彈
enemy_bullets = []
enemy_bullet_speed = 5

# 時間軸
timeline = [
    {"time": 1000, "enemies": 3},  # 1秒時出現3個敵人
    {"time": 3000, "enemies": 5},  # 3秒時出現5個敵人
    {"time": 5000, "enemies": 7},  # 5秒時出現7個敵人
    # 可以在此添加更多事件
]
current_timeline_index = 0
start_time = pygame.time.get_ticks()

# 時鐘
clock = pygame.time.Clock()

# 遊戲主迴圈
running = True
while running:
    screen.fill(BLACK)

    # 處理事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 玩家移動
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_x > 0:
        player_x -= player_speed
    if keys[pygame.K_RIGHT] and player_x < WIDTH - player_size:
        player_x += player_speed
    if keys[pygame.K_UP] and player_y > 0:
        player_y -= player_speed
    if keys[pygame.K_DOWN] and player_y < HEIGHT - player_size:
        player_y += player_speed
  
    # 玩家子彈冷卻
    bullet_cooldown = 200  # 子彈冷卻時間 (毫秒)
    last_bullet_time = pygame.time.get_ticks()

    # 玩家射擊  
    if keys[pygame.K_SPACE]:
        current_time = pygame.time.get_ticks()
        if current_time - last_bullet_time > bullet_cooldown:  # 檢查冷卻
            player_bullets.append([player_x + player_size // 2, player_y])
            last_bullet_time = current_time


    # 更新玩家子彈位置
    for bullet in player_bullets[:]:
        bullet[1] += player_bullet_speed
        if bullet[1] < 0:
            player_bullets.remove(bullet)

    # 時間軸處理
    current_time = pygame.time.get_ticks() - start_time
    if current_timeline_index < len(timeline):
        event = timeline[current_timeline_index]
        if current_time >= event["time"]:
            for _ in range(event["enemies"]):
                enemy_x = random.randint(0, WIDTH - enemy_size)
                enemies.append([enemy_x, 0])
            current_timeline_index += 1

    # 更新敵人位置
    for enemy in enemies[:]:
        enemy[1] += 2
        if enemy[1] > HEIGHT:
            enemies.remove(enemy)
        else:
            # 敵人射擊
            if random.random() < 0.01:  # 隨機發射子彈
                enemy_bullets.append([enemy[0] + enemy_size // 2, enemy[1] + enemy_size])

    # 更新敵人子彈位置
    for bullet in enemy_bullets[:]:
        bullet[1] += enemy_bullet_speed
        if bullet[1] > HEIGHT:
            enemy_bullets.remove(bullet)

    # 碰撞檢測
    for bullet in player_bullets[:]:
        for enemy in enemies[:]:
            if math.hypot(bullet[0] - (enemy[0] + enemy_size // 2), bullet[1] - (enemy[1] + enemy_size // 2)) < enemy_size:
                player_bullets.remove(bullet)
                enemies.remove(enemy)
                break

    for bullet in enemy_bullets[:]:
        if math.hypot(bullet[0] - (player_x + player_size // 2), bullet[1] - (player_y + player_size // 2)) < player_size:
            running = False  # 玩家被擊中，遊戲結束

    # 繪製玩家
    pygame.draw.rect(screen, BLUE, (player_x, player_y, player_size, player_size))

    # 繪製玩家子彈
    for bullet in player_bullets:
        pygame.draw.circle(screen, WHITE, (bullet[0], bullet[1]), 5)

    # 繪製敵人
    for enemy in enemies:
        pygame.draw.rect(screen, RED, (enemy[0], enemy[1], enemy_size, enemy_size))

    # 繪製敵人子彈
    for bullet in enemy_bullets:
        pygame.draw.circle(screen, RED, (bullet[0], bullet[1]), 5)

    # 更新畫面
    pygame.display.flip()

    # 控制遊戲速度
    clock.tick(60)

pygame.quit()
