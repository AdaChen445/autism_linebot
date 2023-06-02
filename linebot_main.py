# -*- coding: UTF-8 -*-
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
from datetime import datetime
from db import *
from autismModel import *


app = Flask(__name__)
# Channel Access Token
line_bot_api = LineBotApi('aDQUjxffx0Fm2wW+SXU+ajS3gg3arGQim0RWA482muRsPOP70HE/kNl1IHxpNy0RDBUwV/c2J7qk5y8f2vptCXLwoc1c5C4kO9HJ8Z272BbBTCUv8rEwoIt9R+d9wNiOF9tWezwsmYQ9+7Eg6vl8QQdB04t89/1O/w1cDnyilFU=')
# Channel Secret
handler = WebhookHandler('56245cd9dcdbb8abfaaced0ab85db506')
# database URL, please re-new this url every time retarting ngrok server
ngrokDBURL = 'https://9c9f-111-251-215-56.ngrok-free.app'

	
@app.route("/callback", methods=['POST'])
def callback():
	signature = request.headers['X-Line-Signature']
	data = request.get_data(as_text=True)
	app.logger.info("Request body: " + data)
	try:
		handler.handle(data, signature)
	except InvalidSignatureError:
		abort(400)
	return 'OK'


@handler.add(MessageEvent)
def handle_message(event):
	reply_content = []
	if event.message.type == 'text':
		if event.message.text in ['同意', '選單']:
			reply_content.append(TemplateSendMessage( 
								alt_text='Buttons template', 
								template=ButtonsTemplate( 
									title='系統功能選單', 
									text='請選擇您想進行的操作\n若需再次叫出此選單請輸入"選單"', 
									actions=[ 
										MessageTemplateAction( 
											label='上傳照片', 
											text='上傳照片' 
										), 
										MessageTemplateAction( 
											label='檢視過往紀錄', 
											text='檢視過往紀錄', 
										), 
										URITemplateAction( 
											label='更多資訊', 
											uri='http://www.autism-hsinchu.org.tw/ap/index.aspx', 
										), 
									] 
								) 
							) )

		elif event.message.text == '上傳照片':
			reply_content.append(TextSendMessage(text='【上傳手寫字相片電子檔操作說明】\n\n照片內容要求：\n1: 手寫字相片內容須為最近一學期內所寫之生字簿\n2: 相片內請勿出現任何非參加測試兒童手寫字以外的痕跡（如：批改痕跡，髒污...\n3: 描寫練習請勿出現在相片內\n4: 手寫字應為兒童自主完成，家長不應進行輔助\n \n上傳要求：\n1: 上傳之相片電子檔規格限定JPG、JPEG或PNG格式，色彩模式為RGB，檔案大小不得大於5MB，解析度至少需達531像素，寬度至少需達413像素。\n2: 同一用戶同一天僅能上傳相片電子檔5次，上傳後檔案僅用於系統檢測不會進行其他使用。'))
			exampleImageURL = f'{ngrokDBURL}/exampleImage.jpg'
			reply_content.append(ImageSendMessage(
									original_content_url=exampleImageURL,
									preview_image_url=exampleImageURL
								))

		elif event.message.text == '檢視過往紀錄':
			imageURLs = read_record(event.source.user_id, ngrokDBURL)
			
			for imageURL in imageURLs:
				reply_content.append(ImageSendMessage(
									original_content_url=imageURL,
									preview_image_url=imageURL
								))

		elif event.message.text == '不同意':
			reply_content.append(TextSendMessage(text='感謝您使用本系統，有緣再相見'))

		else:
			reply_content.append(TextSendMessage(text='若需使用本系統服務，請輸入"選單"'))

	elif event.message.type == 'image':
		timeStamp = datetime.fromtimestamp(round(int(event.timestamp)*0.001)).strftime("%Y-%m-%d--%H-%M-%S")
		imageContent = line_bot_api.get_message_content(event.message.id)
		imageName = f'{timeStamp}.jpg'
		userID = event.source.user_id

		img = write_temp_image(userID, imageContent)
		result = model_classify(img)
		# result = '陰性' # demo時避免當機使用

		imageContent = line_bot_api.get_message_content(event.message.id)
		write_record(userID, imageName, imageContent, result, timeStamp)
		reply_content.append(TextSendMessage(text=f'您的檢測結果為【{result}】'))
	
	line_bot_api.reply_message(event.reply_token, reply_content)


@handler.add(FollowEvent)
def welcome(event):
	print(event)
	userID = event.source.user_id
	create_member(userID)

	reply_content = []
	reply_content.append(TextSendMessage(text='臺灣醫療品質與照護體系全球有目共睹，但在山地、離島地區，就醫可近性或醫療量能都遠不及都會地區。根據美國疾病控制與預防中心自閉癥和發育障礙監測網絡(ADDM)的估計，大約每36名8歲兒童中就有1名被確診為自閉症。根據衛生福利部身心障礙者人數統計表2022年第四季報表顯示，2023年台灣自閉症人數最新資料是19,078人。'))
	reply_content.append(TextSendMessage(text='為使偏鄉離島居民同樣獲得周全的醫療照顧，特別是偏鄉兒童（家長）正面臨著醫療資源不足，精神檢測意識不足的困境。我們提供的線上自閉症評估快篩Linebot，是一種針對偏鄉兒童自我精神評估的工具，具有可快速在家進行自閉症初步診斷的特點，能夠幫助我們他們在醫療資源有限的情況下，進行學齡前自閉症篩檢。'))
	reply_content.append(TextSendMessage(text='本系統通過結合深度學習與電腦視覺領域的技術對兒童手寫字進行評估分析，故需要您提供兒童手寫字相片，在此過程中可能會涉及您個人資料的收集。為提供更好、更個人化的服務，我們將會為您上傳的相片及分析結果建檔，您可以在未來任何時間調閱您的檢測紀錄。本應用不會出售、出租或任意交換任何您的個人資料給其他團體或個人。'))
	reply_content.append(
		TemplateSendMessage( 
						alt_text='Buttons template', 
						template=ButtonsTemplate( 
							title='使用者知情同意書', 
							text='請問您是否同意此系統基於醫療檢測需求蒐集您的個人資料?', 
							actions=[ 
								MessageTemplateAction( 
									label='同意', 
									text='同意' 
								), 
								MessageTemplateAction( 
									label='不同意', 
									text='不同意', 
								),
							])
						))
	line_bot_api.reply_message(event.reply_token, reply_content)


import os
if __name__ == "__main__":
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port=port)