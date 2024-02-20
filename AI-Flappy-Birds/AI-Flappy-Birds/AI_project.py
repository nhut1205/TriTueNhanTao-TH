import random  
import sys  
import pygame  # Thư viện để tạo game
from pygame.locals import *  # Import các hằng số và sự kiện từ pygame
import numpy  
import matplotlib.pyplot as plt  # Thư viện để vẽ biểu đồ

SW = 280  
SH = 511 

matDat = SH * 0.8  
IMAGES = {}
pygame.font.init()
WINDOW = pygame.display.set_mode((SW, SH)) 
Font = pygame.font.SysFont("comicsans", 30)
BIRD = 'imgs/bird1.png' 
BG = 'imgs/bg.png' 
PIPE = 'imgs/pipe.png' 
Q = numpy.zeros((7, 21, 2), dtype=float)  
FPS = 32 

#Hàm liên quan đến trò chơi
def static():
    # Hàm để hiển thị màn hình ban đầu với thông tin trò chơi
    birdxpos = int(SW/5)  # Vị trí ban đầu của con chim theo chiều ngang
    birdypos = int((SH - IMAGES['bird'].get_height()) / 2) 
    basex = 0  # Vị trí ban đầu của mặt đất

    while (True):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                return
            else:
                # Vẽ nền, con chim, mặt đất và thông tin trò chơi
                WINDOW.blit(IMAGES['background'], (0, 0))
                WINDOW.blit(IMAGES['bird'], (birdxpos, birdypos))
                WINDOW.blit(IMAGES['base'], (basex, matDat))
                text1 = Font.render("AI PROJECT", 1, (255, 255, 255))
                text2 = Font.render("NHUT PROJECT", 1, (255, 255, 255))
                WINDOW.blit(text1, (SW / 2, SH / 2))
                WINDOW.blit(text2, (10, 50))
                pygame.display.update()
                FPSCLOCK.tick(FPS)


def game_start(generation,x,y):
	# Hàm chính thể hiện vòng lặp chính của trò chơi, trong đó con chim được điều khiển bởi Q-learning
	score = 0  # Điểm của trò chơi
	birdxpos = int(SW / 5)  
	birdypos = int(SH / 2)  
	basex1 = 0  
	basex2 = SW 

	bgx1 = 0  # Vị trí ban đầu của nền (phần 1)
	bgx2 = IMAGES['background'].get_width()  # Vị trí ban đầu của nền (phần 2)

	newPipe1 = taoOng()  # Tạo ống mới
	newPipe2 = taoOng()  # Tạo ống mới

	#Danh sách ống nước phía trên trò chơi
	up_pipes = [
	{'x':SW +200,'y': newPipe1[0]['y']},
	{'x':SW +500 ,'y': newPipe2[0]['y']}
	]

	#Danh sách ống nước phía dưới trò chơi 
	bttm_pipes = [
	{'x':SW+200,'y':newPipe1[1]['y']},
	{'x':SW +500 ,'y': newPipe2[1]['y']}
	]

	pipeVelx = -4  # Tốc độ di chuyển của ống

	birdyvel = -5 
	birdymaxvel = 10  
	birdyvelmin = -8  
	birdyacc = 1  

	playerFlapAccv = -8  # Gia tốc khi con chim nhảy lên
	playerFlapped = False
	
	while(True):
	
		x_prev,y_prev = trangThai(birdxpos,birdypos,bttm_pipes)

		# Xác định xem AI có nên nhảy dựa trên quyết định của Q-learning

		jump = ai_play(x_prev,y_prev)

		for event in pygame.event.get():
			if event.type == QUIT:
				plt.scatter(x,y)
				plt.xlabel("GENERATION/Number of Trials")
				plt.ylabel("SCORE")
				plt.title("Flappy Birds : AI Project")
				plt.show()
				pygame.quit()
				sys.exit()
				
		if jump:
			if birdypos>0:
				birdyvel = playerFlapAccv
				playerFlapped = True
		
		# Phát hiện điểm khi đi qua ống
		playerMidPos= birdxpos + IMAGES['bird'].get_width()/2
		for pipe in up_pipes:
			pipeMidPos = pipe ['x'] +IMAGES['pipe'][0].get_width()/2
			if pipeMidPos <= playerMidPos < pipeMidPos +4 :
				score += 1

		# Cập nhật tốc độ di chuyển của con chim khi không nhảy và không vượt quá tốc độ tối đa
		if birdyvel < birdymaxvel and not playerFlapped:
			birdyvel += birdyacc

		if playerFlapped:
			playerFlapped = False
		# Lấy chiều cao của hình ảnh con chim
		playerHeight = IMAGES['bird'].get_height()
		# Cập nhật vị trí dọc của con chim dựa trên tốc độ hiện tại và trọng lực
		birdypos = birdypos + min (birdyvel, matDat - birdypos -playerHeight)
		# Cập nhật vị trí của ống nước phía trên và phía dưới
		for upperPipe,lowerPipe in zip(up_pipes,bttm_pipes):
			upperPipe['x'] += pipeVelx
			lowerPipe['x'] += pipeVelx
		# Kiểm tra xem ống nước phía trên đầu tiên đã đi qua màn hình chưa
		if (0<up_pipes[0]['x']<5):
			newPipe = taoOng()
			up_pipes.append(newPipe[0])
			bttm_pipes.append(newPipe[1])
		# Kiểm tra xem ống nước phía trên đầu tiên đã đi qua màn hình chưa
		if(up_pipes[0]['x'] < -IMAGES['pipe'][0].get_width() ):
	    # Loại bỏ ống nước phía trên và phía dưới khỏi danh sách
			up_pipes.pop(0)
			bttm_pipes.pop(0)
		basex1-=4
		basex2-=4
		if(basex1 <= -IMAGES['base'].get_width()):
			basex1 = basex2
			basex2 = basex1 + IMAGES['base'].get_width()
		bgx1-=2
		bgx2-=2
		if(bgx1 <= -IMAGES['background'].get_width()):
			bgx1 = bgx2
			bgx2 = bgx1 + IMAGES['background'].get_width()
	    
		# Phát hiện va chạm và thưởng điểm
		crashTest = KiemTraVaCham(birdxpos,birdypos,up_pipes,bttm_pipes)
		x_new,y_new = trangThai(birdxpos,birdypos,bttm_pipes)
		if crashTest:
			reward = -1000
			capnhatQ(x_prev,y_prev,jump,reward,x_new,y_new)
			return score

		reward = 15

		capnhatQ(x_prev,y_prev,jump,reward,x_new,y_new)

		WINDOW.blit(IMAGES['background'],(bgx1,0))
		WINDOW.blit(IMAGES['background'],(bgx2,0))
		for upperPipe,lowerPipe in zip(up_pipes,bttm_pipes):
			WINDOW.blit(IMAGES['pipe'][0],(upperPipe['x'],upperPipe['y']))
			WINDOW.blit(IMAGES['pipe'][1],(lowerPipe['x'],lowerPipe['y']))
		WINDOW.blit(IMAGES['base'],(basex1,matDat))
		WINDOW.blit(IMAGES['base'],(basex2,matDat))
		text1 = Font.render("Score: "+ str(score),1,(255,255,255))
		text2 = Font.render("Generation: "+ str(generation),1,(255,255,255))
		WINDOW.blit(text1,(SW - 10 -text1.get_width(),10))
		WINDOW.blit(text2,(0,0))
		WINDOW.blit(IMAGES['bird'],(birdxpos,birdypos))

		pygame.display.update()
		FPSCLOCK.tick()

#Kiểm tra va chạm giữa chim và ống để đưa ra quyết định
def KiemTraVaCham(birdxpos,birdypos,up_pipes,bttm_pipes):

#Kiểm tra vị trí của chim
#Chiều cao đang bay
	if (birdypos >= matDat - IMAGES['bird'].get_height() or birdypos < 0):
		return True

#ống trên
	for pipe in up_pipes:
		pipeHeight = IMAGES['pipe'][0].get_height()
		if(birdypos < pipeHeight + pipe['y'] and abs(birdxpos - pipe['x']) < IMAGES['pipe'][0].get_width()):
			return True
#ống dưới 
	for pipe in bttm_pipes:
		if (birdypos + IMAGES['bird'].get_height() > pipe['y'] and abs(birdxpos - pipe['x']) < IMAGES['pipe'][0].get_width()):
			return True
	return False

#Tạo ống nước random
def taoOng():

	pipeHeight = IMAGES['pipe'][1].get_height()
	gap = int(SH/4)
	y2 = int(gap + random.randrange(0,int(SH - IMAGES['base'].get_height() - 1.2*gap)))
	pipex = int(SW+300 )
	y1 = int(pipeHeight -y2 +gap)

	pipe = [
	{'x':pipex,'y':-y1},
	{'x':pipex,'y':y2}
	]
	return pipe

#Chim tự động bay dựa vào thuật toán Q Learning 
def ai_play(x,y):
	max=0
	jump = False
	
	
	if(Q[x][y][1]>Q[x][y][0]):
		max = Q[x][y][1]
		jump =True

	return jump

#Cập nhật trạng thái hiện tại của flappybirth
def trangThai(birdxpos,birdypos,bttm_pipes):
	# Chuyển đổi vị trí của con chim và ống thành trạng thái Q-learning
	x = min(280, bttm_pipes[0]['x'])
	y = bttm_pipes[0]['y']-birdypos
	if(y<0):
		y=abs(y)+408
	return int(x/40-1),int(y/40)

#Trả về giá trị của Q Learning
def capnhatQ(x_prev,y_prev,jump,reward,x_new,y_new):
	# Cập nhật Q-learning dựa trên chuyển trạng thái, hành động, điểm thưởng và trạng thái mới 
	if jump:
	# Nếu quyết định là nhảy, cập nhật Q-value cho hành động nhảy
		Q[x_prev][y_prev][1] = 0.4 * Q[x_prev][y_prev][1] + (0.6)*(reward+max(Q[x_new][y_new][0],Q[x_new][y_new][1]))
	else :
	# Nếu không nhảy, cập nhật Q-value cho hành động không nhảy
		Q[x_prev][y_prev][0] = 0.4 * Q[x_prev][y_prev][0] + (0.6)*(reward+max(Q[x_new][y_new][0],Q[x_new][y_new][1]))


    # Vẽ nền và các đối tượng trò chơi
if __name__=="__main__":

	pygame.init()
	FPSCLOCK = pygame.time.Clock()
	pygame.display.set_caption("AI PROJECT")

	IMAGES['base'] = pygame.image.load('imgs/base.png').convert_alpha()
	IMAGES['pipe'] = ( pygame.transform.rotate(pygame.image.load(PIPE).convert_alpha(),180) , pygame.image.load(PIPE).convert_alpha())
	IMAGES['background']= pygame.image.load(BG).convert()
	IMAGES['bird'] = pygame.image.load(BIRD).convert_alpha()
	generation = 1
	static()
	x=[]
	y=[]
	while(True):
		score = game_start(generation,x,y)
		if (score==-1):
			break
		x.append(generation)
		y.append(score)
		generation+=1

	print(generation)


