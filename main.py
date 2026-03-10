import pygame
import random
import math


# Game Initialiazation
pygame.init()
screen = pygame.display.set_mode((1200, 1500))
clock = pygame.time.Clock()
running = True
gameState = "start"
dt = 0
score = 0

scoreFont = pygame.font.SysFont("arial", 80, bold = True)
menuFont = pygame.font.SysFont("arial", 100, bold = True)
smallFont = pygame.font.SysFont("arial", 50)

# Load/Section Crystal Sprite Sheet (0 - Idle, 1 - Up, 2 - Down)
crystalSpriteSheet = pygame.image.load("assets/crystalSprites.png").convert_alpha()

crystalSheetWidth = crystalSpriteSheet.get_width()
crystalSheetHeight = crystalSpriteSheet.get_height()

stateCount = 3
framePerState = 4

frameHeight = crystalSpriteSheet.get_height() // stateCount
frameWidth = crystalSpriteSheet.get_width() // framePerState

crystalSheetY = 0

crystalSprites = {
    "frame1" : crystalSpriteSheet.subsurface(0, crystalSheetY, frameWidth, frameHeight),
    "frame2" : crystalSpriteSheet.subsurface(frameWidth, crystalSheetY, frameWidth, frameHeight),
    "frame3" : crystalSpriteSheet.subsurface(2 * frameWidth, crystalSheetY, frameWidth, frameHeight),
    "frame4" : crystalSpriteSheet.subsurface(3 * frameWidth, crystalSheetY, frameWidth, frameHeight)
}

# Scale Crystal
crystalSprites["frame1"] = pygame.transform.scale(crystalSprites["frame1"], (160, 160))
crystalSprites["frame2"] = pygame.transform.scale(crystalSprites["frame2"], (160, 160))
crystalSprites["frame3"] = pygame.transform.scale(crystalSprites["frame3"], (160, 160))
crystalSprites["frame4"] = pygame.transform.scale(crystalSprites["frame4"], (160, 160))

idleFrames = [
    crystalSprites["frame1"],
    crystalSprites["frame2"],
    crystalSprites["frame3"],
    crystalSprites["frame4"]
]

# Particle Trail
trailTimer = 0
trailInterval = 0.03

particles = []
def spawn_trail(x, y):
    life = random.uniform(0.2, 0.5)

    particles.append({
        "x": x,
        "y": y,
        "vx": random.uniform(-120, -40),
        "vy": random.uniform(-30, 30),
        "size": random.randint(4, 8),
        "life": life,
        "maxLife": life,
        "color": random.choice([
            (120, 240, 255),
            (100, 200, 255),
            (180, 120, 255)
        ])
    })

# Load Background
bckgrndImg = pygame.image.load("assets/Background.png").convert_alpha()
bckgrndImg = pygame.transform.scale(bckgrndImg, (screen.get_width(), screen.get_height()))

# Load Tiles Sheet
tilesImgSheet = pygame.image.load("assets/tiles.png").convert_alpha()

# Section Pillars [0 - Green, 1 - Yellow, 2 - Red, 3 - Blue]
pillarSprites = [
    {
        "pillarTop" : tilesImgSheet.subsurface((0, 0, 32, 16)),
        "pillarBody" : tilesImgSheet.subsurface((0, 16, 32, 16)),
        "pillarBottom" : tilesImgSheet.subsurface((0, 32, 32, 16))
    },
    {
        "pillarTop" : tilesImgSheet.subsurface((32, 0, 32, 16)),
        "pillarBody" : tilesImgSheet.subsurface((32, 16, 32, 16)),
        "pillarBottom" : tilesImgSheet.subsurface((32, 32, 32, 16))
    },
    {
        "pillarTop" : tilesImgSheet.subsurface((64, 0, 32, 16)),
        "pillarBody" : tilesImgSheet.subsurface((64, 16, 32, 16)),
        "pillarBottom" : tilesImgSheet.subsurface((64, 32, 32, 16))
    },
    {
        "pillarTop" : tilesImgSheet.subsurface((96, 0, 32, 16)),
        "pillarBody" : tilesImgSheet.subsurface((96, 16, 32, 16)),
        "pillarBottom" : tilesImgSheet.subsurface((96, 32, 32, 16))
    }
]

# Scale Pillars
for color in pillarSprites:
    color["pillarTop"] = pygame.transform.scale(color["pillarTop"], (158, 80))
    color["pillarBody"] = pygame.transform.scale(color["pillarBody"], (158, 80))
    color["pillarBottom"] = pygame.transform.scale(color["pillarBottom"], (158, 80))

# Section Ground
groundHeight = 160
groundY = screen.get_height() - groundHeight

groundTile01 = tilesImgSheet.subsurface((0, 48, 16, 16))
groundTile02 = tilesImgSheet.subsurface((0, 48, 16, 16))
groundTile03 = tilesImgSheet.subsurface((0, 48, 16, 16))
groundTile04 = tilesImgSheet.subsurface((0, 48, 16, 16))
groundTile05 = tilesImgSheet.subsurface((0, 48, 16, 16))
groundTile06 = tilesImgSheet.subsurface((0, 48, 16, 16))
groundTile1 = tilesImgSheet.subsurface((16, 48, 16, 16))
groundTile2 = tilesImgSheet.subsurface((32, 48, 16, 16))

groundVariants = [
    groundTile01, groundTile02, groundTile03, groundTile04, groundTile05, groundTile06, groundTile1, groundTile2
]

for i in range(len(groundVariants)):
    groundVariants[i] = pygame.transform.scale(groundVariants[i], (80, 80))



def randomizeGround(): 
    newGroundTiles = []
    
    y = groundY
    while y < screen.get_height():
        x = 0
        while x < screen.get_width():
            newGroundTiles.append({
                "x": x,
                "y": y,
                "variant": random.randint(0, len(groundVariants) - 1)
            })
            x += groundVariants[0].get_width()
        y += groundVariants[0].get_height()
    return newGroundTiles

groundTiles = randomizeGround()

# Tile Pillars Function
def make_tiled_pipe(top, body, bottom, width, height):
    pipe_surface = pygame.Surface((width, height), pygame.SRCALPHA)

    y = 0
    pipe_surface.blit(top, (0, y))
    y += top.get_height()

    while y < height - bottom.get_height():
        pipe_surface.blit(body, (0, y))
        y += body.get_height()

    pipe_surface.blit(bottom, (0, height - bottom.get_height()))

    return pipe_surface

# Player Variables
playerWidth = 160
playerHeight = 80
playerPos = pygame.Vector2(screen.get_width()/4, screen.get_height()/2)

playerVelocity = 0
gravity = 2500
jumpStrength = -700

# Pipe Variables
pipeWidth = 158
gapHeight = 300
pipeSpeed = 350

pipeCount = 3
pipeDistance = 530
marginTop = 300
marginBottom = 460

def create_pipes():
    pipes = []
    for i in range(pipeCount):
        pipes.append({
            "x": screen.get_width() + i * pipeDistance,
            "gapY": random.randint(marginTop, screen.get_height() - marginBottom),
            "passed": False,
            "variant": random.randint(0, len(pillarSprites) - 1)
        })
    return pipes

pipes = create_pipes()

# Reset Function
def reset_run():
    global score, playerPos, playerVelocity, pipes, groundTiles, particles, trailTimer
    score = 0
    playerPos = pygame.Vector2(screen.get_width() / 4, screen.get_height() / 2)
    playerVelocity = 0
    pipes = create_pipes()
    groundTiles = randomizeGround()
    particles = []
    trailTimer = 0

# Particle Function
def update_particles():
            
            global trailTimer

            trailCount = 1
            if abs(playerVelocity) > 400:
                trailCount = 2
            if abs(playerVelocity) > 800:
                trailCount = 3

            trailTimer += dt
            while trailTimer >= trailInterval:
                for _ in range(trailCount):
                    spawn_trail(playerPos.x - 50, playerPos.y)
                trailTimer -= trailInterval

            for particle in particles[:]:
                particle["x"] += particle["vx"] * dt
                particle["y"] += particle["vy"] * dt
                particle["life"] -= dt
                particle["size"] *= 0.98

                if particle["life"] <= 0:
                    particles.remove(particle)

# Draw World Function
def draw_world():
    # Draw Screen Background
    screen.blit(bckgrndImg, (0, 0))

    # Pipes
    for pipe in pipes:
        
        topPipeHeight = pipe["gapY"] - gapHeight / 2
        bottomPipeY = pipe["gapY"] + gapHeight / 2
        bottomPipeHeight = screen.get_height() - bottomPipeY - groundHeight

        topPillarImg = make_tiled_pipe(
            pillarSprites[pipe["variant"]]["pillarTop"],
            pillarSprites[pipe["variant"]]["pillarBody"],
            pillarSprites[pipe["variant"]]["pillarBottom"],
            pipeWidth,
            int(topPipeHeight)
        )
            
        bottomPillarImg = make_tiled_pipe(
            pillarSprites[pipe["variant"]]["pillarTop"],
            pillarSprites[pipe["variant"]]["pillarBody"],
            pillarSprites[pipe["variant"]]["pillarBottom"],
            pipeWidth,
            int(bottomPipeHeight)
        )

        screen.blit(topPillarImg, (pipe["x"], 0))
        screen.blit(bottomPillarImg, (pipe["x"], bottomPipeY))
        
    # Draw Ground Tiles
    for tile in groundTiles:
        screen.blit(groundVariants[tile["variant"]], (tile["x"], tile["y"]))

    # Draw Crystal + Particle Trail
    for particle in particles:

        alpha = max(0, min(255, int((particle["life"] / particle["maxLife"]) * 255)))
        size = max(1, int(particle["size"]))

        surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)

        pygame.draw.circle(
            surf,
            (*particle["color"], alpha),
            (size, size),
            size
        )

        screen.blit(surf, (particle["x"] - size, particle["y"] - size))
        
    idleFrameIndex = (pygame.time.get_ticks() // 120) % len(idleFrames)
    currentCrystal = idleFrames[idleFrameIndex]

    floatOffset = math.sin(pygame.time.get_ticks() * 0.005) * 4
    rotation = max(-30, min(45, playerVelocity * 0.05))
    rotatedBird = pygame.transform.rotate(currentCrystal, -rotation)

    rect = rotatedBird.get_rect(center=(playerPos.x, playerPos.y + floatOffset))
    screen.blit(rotatedBird, rect)
        
    # Score Display
    scoreText = scoreFont.render(str(score), True, "white")
    scoreRect = scoreText.get_rect(center=(screen.get_width() / 2, 50))
    screen.blit(scoreText, scoreRect)

def get_crystal_rect():
    hitboxW = 100
    hitboxH = 50

    return pygame.Rect(
        int(playerPos.x - hitboxW / 2),
        int(playerPos.y - hitboxH / 2),
        hitboxW,
        hitboxH
    )

# Game Loop
while running:
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Jump Mechanic
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and gameState == "playing":
                playerVelocity = jumpStrength

            # Start Game
            if event.key == pygame.K_SPACE and gameState == "start":
                gameState = "playing"

            # Restart Game  
            if event.key == pygame.K_r and gameState == "game_over":
                reset_run()
                gameState = "playing"   

    if gameState == "playing":

        # Crystal Physics
        playerVelocity += gravity * dt
        playerPos.y += playerVelocity * dt
        
        # Particle Trail
        update_particles()
        
        # Pipe Mechanic + Score + Reset
        for pipe in pipes:
            pipe["x"] -= pipeSpeed * dt

            # Score Count
            if not pipe["passed"] and pipe["x"] + pipeWidth < playerPos.x:
                pipe["passed"] = True
                score += 1

            # Reset
            if pipe["x"] + pipeWidth < 0:
                rightmostX = max(p["x"] for p in pipes)
                pipe["x"] = rightmostX + pipeDistance
                pipe["gapY"] = random.randint(marginTop, screen.get_height() - marginBottom)
                pipe["passed"] = False
                pipe["variant"] = random.randint(0, len(pillarSprites) - 1)

            # Collision
            topPipeHeight = pipe["gapY"] - gapHeight / 2
            bottomPipeY = pipe["gapY"] + gapHeight / 2
            bottomPipeHeight = screen.get_height() - bottomPipeY - groundHeight

            topRect = pygame.Rect(int(pipe["x"]), 0, pipeWidth, int(topPipeHeight))
            bottomRect = pygame.Rect(int(pipe["x"]), int(bottomPipeY), pipeWidth, int(bottomPipeHeight))
                    
            if get_crystal_rect().colliderect(topRect) or get_crystal_rect().colliderect(bottomRect):
                    gameState = "game_over"
                    
        # Border Collision
        if playerPos.y + playerHeight / 2 >= groundY:
            gameState = "game_over"
            
        if playerPos.y - playerHeight / 2 <= 0:
            gameState = "game_over"  

    if gameState == "start":
        screen.blit(bckgrndImg, (0, 0))

        titleText = menuFont.render("FLAPPY AI", True, "white")
        titleRect = titleText.get_rect(center=(screen.get_width() / 2, screen.get_height() / 2 - 120))
        screen.blit(titleText, titleRect)

        startText = smallFont.render("Press SPACE to Start", True, "white")
        startRect = startText.get_rect(center=(screen.get_width() / 2, screen.get_height() / 2))
        screen.blit(startText, startRect)
    elif gameState == "game_over":
        draw_world()
        
        gameOverText = menuFont.render("GAME OVER", True, "white")
        gameOverRect = gameOverText.get_rect(center=(screen.get_width() / 2, screen.get_height()/2 - 100))
        screen.blit(gameOverText, gameOverRect)

        restartText  = smallFont.render("Press R to Restart", True, "white")
        restartRect = restartText.get_rect(center=(screen.get_width() / 2, screen.get_height()/2))
        screen.blit(restartText, restartRect)

        finalScoreText = smallFont.render(f"Score: {score}", True, "white")
        finalScoreRect = finalScoreText.get_rect(center=(screen.get_width() / 2, screen.get_height()/2 + 75))
        screen.blit(finalScoreText, finalScoreRect)
    elif gameState == "playing":
        draw_world()

    pygame.display.flip()
    dt = clock.tick(60) / 1000
   
pygame.quit()