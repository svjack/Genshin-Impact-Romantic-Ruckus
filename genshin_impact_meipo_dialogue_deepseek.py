# coding:utf-8

'''
pip install openai
pip install sentence_transformers
pip install pandas
pip install langchain
pip install faiss-cpu
pip install huggingface_hub
pip install datasets
'''

import os
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

import pandas as pd
import numpy as np
import os
import json

from langchain.vectorstores import FAISS
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain import chains

from huggingface_hub import snapshot_download

##### deepseek openai client
from openai import OpenAI
with open(".cache/DeepSeek-key.txt", "r") as f:
    key = f.read().strip()
client = OpenAI(api_key=key,
                base_url="https://api.deepseek.com")


all_characters_in_settings = ['丽莎', '行秋', '优菈', '魈', '五郎', '钟离', '温迪',
'菲谢尔', '诺艾尔', '云堇',
 '班尼特', '安柏', '莫娜', '柯莱', '迪卢克', '绮良良', '阿贝多', '卡维', '提纳里',
 '夏沃蕾', '鹿野院平藏', '辛焱', '八重神子', '凝光', '九条裟罗', '米卡', '刻晴',
 '罗莎莉亚', '甘雨', '砂糖', '坎蒂丝', '枫原万叶', '雷电将军', '白术', '娜维娅',
 '芙宁娜', '莱欧斯利', '迪奥娜', '夜兰', '久岐忍', '菲米尼', '可莉', '流浪者',
 '多莉', '凯亚', '琴', '琳妮特', '荒泷一斗', '神里绫人', '夏洛蒂', '雷泽', '芭芭拉',
 '珊瑚宫心海', '妮露', '七七', '香菱', '珐露珊', '赛诺', '神里绫华', '申鹤', '瑶瑶',
 '达达利亚', '早柚', '北斗', '重云', '林尼', '埃洛伊', '托马', '纳西妲', '烟绯',
 '那维莱特', '迪希雅', '宵宫', '胡桃', '艾尔海森', '莱依拉']

girls = ['丽莎', '优菈',
 '菲谢尔', '诺艾尔', '云堇',
   '安柏', '莫娜', '柯莱', '绮良良',
  '夏沃蕾',  '辛焱', '八重神子', '凝光', '九条裟罗', '刻晴',
  '罗莎莉亚', '甘雨', '砂糖', '坎蒂丝', '雷电将军', '娜维娅',
  '芙宁娜', '迪奥娜', '夜兰', '久岐忍', '可莉',
  '多莉', '琴', '琳妮特', '夏洛蒂', '芭芭拉',
  '珊瑚宫心海', '妮露', '七七', '香菱', '珐露珊','神里绫华', '申鹤', '瑶瑶',
  '早柚', '北斗', '埃洛伊', '纳西妲', '烟绯',
  '迪希雅', '宵宫', '胡桃', '莱依拉']

dialogue_dict = {'剧情1': '\n1. **媒婆：你啥情况** - 媒婆询问男孩的近况。\n2. **男孩：坐了5年牢刚放出来呀** - 男孩回答自己刚从监狱释放，坐了5年牢。\n3. **媒婆：这管得严\x05年都没接触过女孩子\\没有什么感情经历** - 媒婆提到监狱管理严格，男孩在狱中没有机会接触女性，缺乏感情经历。\n4. **女孩：这可不多见阿姨** - 女孩对男孩的经历表示惊讶。\n5. **媒婆：嗯** - 媒婆回应。\n6. **媒婆：问你现在啥工作** - 媒婆询问男孩的工作情况。\n7. **男孩：我这情况又不好找工作\\打打麻将赢个饭钱呀** - 男孩表示自己的背景不利于找工作，通过打麻将赚取生活费。\n8. **媒婆：这孩子聪明\\喜欢智力的碰撞\\那吃饭家伙就是这** - 媒婆称赞男孩聪明，喜欢智力游戏，打麻将是他谋生的手段。\n9. **媒婆：那你屋里是啥情况** - 媒婆询问男孩的家庭情况。\n10. **男孩：我妈是植物人** - 男孩回答自己的母亲是植物人。\n11. **媒婆：他妈特别好相处\\不咋爱说话\\没事就爱睡睡觉** - 媒婆描述男孩的母亲容易相处，不爱说话，喜欢睡觉。\n12. **女孩：这家庭氛围可以啊** - 女孩对家庭氛围表示认可。\n13. **女孩：那她性格怎么样** - 女孩询问男孩的性格。\n14. **媒婆：问你性格咋样** - 媒婆再次询问男孩的性格。\n15. **男孩：我脾气暴躁\\一急就爱打人\\要不然我不会进去啊** - 男孩承认自己脾气暴躁，容易在情绪激动时打人，解释自己入狱的原因。\n16. **媒婆：他性格开朗有个性\\喜欢直来直去的\\不像其他男孩子相处起来这么费劲\\啥都得叫你猜** - 媒婆描述男孩性格直率，容易相处，不喜欢猜疑。\n17. **女孩：嗯\\就是我性子直也猜不来** - 女孩确认自己性格直率，不喜欢猜疑。\n18. **女孩：姨这彩礼** - 女孩开始讨论彩礼问题。\n19. **媒婆：问彩礼呢** - 媒婆回应彩礼问题。\n20. **男孩：彩礼300抽\\屋里条件不好\\就只望着彩礼呢** - 男孩提出彩礼金额，表示家庭条件不佳，依赖彩礼。\n21. **媒婆：彩礼他要500抽\\这我能答应吗\\我直接给你讲到300抽** - 媒婆提到对方要求的彩礼金额，试图说服男孩接受300抽的彩礼。\n22. **女孩：这么多啊** - 女孩对彩礼金额表示惊讶。\n23. **媒婆：不多** - 媒婆强调彩礼金额不多。\n24. **媒婆：这不一小半都给你讲下去了吗\\人家养大个男娃也不容易咧\\姨都看了\\这小伙也是一个实打实过日子的\\以后你们结了婚齐心干一年了\\就给挣回来了** - 媒婆强调已经降低了彩礼金额，表示理解对方家庭的辛苦，认为男子是踏实过日子的人，建议婚后共同努力赚回彩礼。\n25. **女孩：行\\姨定了吧** - 女孩同意媒婆的建议。\n26. **媒婆：对嘛** - 媒婆确认决定。\n27. **媒婆：姨一看就是聪明娃\\走定** - 媒婆称赞男孩聪明并决定此事。\n',
 '剧情2': '\n1. **媒婆：你有多高** - 媒婆询问男孩的身高。\n2. **男孩：1米6** - 男孩回答自己的身高。\n3. **媒婆：蹦一下** - 媒婆开玩笑地让男孩跳一下。\n4. **媒婆：蹦起来能有好几米，排场得很** - 媒婆幽默地介绍男孩的身高。\n5. **女孩：嗯** - 媒婆称赞男孩唱歌好听。\n6. **媒婆：你经济情况咋样** - 媒婆询问男孩的经济状况。\n7. **男孩：我是我们村最穷的\\我爸欠了几百万的债** - 男孩自嘲地说自己是村里最穷的，男孩提到父亲欠债的情况。\n8. **媒婆：富二代\\他爸是当地首富\\和各大金融机构都有往来\\看的都是几百万的生意** - 媒婆指出男孩其实是富二代，媒婆详细描述男孩父亲的经济实力和生意规模。\n9. **女孩：这么厉害呀\\那他具体是做什么工作的** - 女孩对男孩的家庭背景表示惊讶和赞赏，询问男孩的具体工作。\n10. **媒婆：问你具体是做啥工作的** - 媒婆问男孩工作。\n11. **男孩：在璃月当保安** - 男孩开玩笑地说自己在璃月当保安。\n12. **媒婆：做的是进出口的生意\\可有本事了** - 媒婆纠正并称赞男孩实际从事的是进出口生意，很有能力。\n13. **媒婆：你有啥兴趣爱好** - 媒婆询问男孩的兴趣爱好。\n14. **男孩：我爱画大饼** - 男孩回答自己的兴趣爱好是画大饼。\n15. **媒婆：你这算啥爱好呢嘛\\你这不好寻不好寻** - 媒婆对男孩的爱好表示不解。\n16. **媒婆：哎呀\\不要不要** - 媒婆试图推卸男孩的贿赂。\n17. **媒婆：他是画家\\话也特别值钱\\跟着他不愁吃不愁喝\\还能给你提供情绪价值** - 媒婆描述男孩实际上是一位画家，作品价值高，生活无忧，能提供情绪支持。\n18. **女孩：听着是不错** - 女孩对男孩的情况表示满意。\n19. **媒婆：咱们都是时辰亲戚\\我要不是你二舅妈\\娘家姨的外甥女儿\\我也不会把她介绍给你\\这可都是抢手货** - 媒婆强调与女孩的亲戚关系，解释为何介绍男孩给女孩，并称男孩是抢手货。\n20. **媒婆：怎么样\\定了吧** - 媒婆询问女孩是否同意这门亲事。\n21. **媒婆：嗯\\走啊定啊** - 媒婆带着女孩决定此事。\n',
 '剧情3': '\n1. **媒婆：你啥情况** - 媒婆询问男孩的恋爱经历。\n2. **男孩：之前谈了三个\\三个都没了哈** - 男孩回答自己之前谈过三个女朋友，但都分手了。\n3. **女孩：你不会真克妻吧** - 女孩开玩笑地问男孩是否克妻。\n4. **男孩：一点点吧** - 男孩自嘲地承认可能有点克妻。\n5. **媒婆：男娃特别真诚\\也没有什么要求\\就是你得穿耐克** - 媒婆介绍男孩真诚，没有特别要求，只是希望女孩穿耐克。\n6. **媒婆：你再介绍一下你的兴趣爱好** - 媒婆询问男孩的兴趣爱好。\n7. **男孩：我就喜欢这（做抽烟姿势）哦\\还有这（做喝酒姿势）\\来啊** - 男孩展示自己的兴趣爱好是抽烟和喝酒。\n8. **媒婆：不了不了不了** - 媒婆对男孩的兴趣爱好表示拒绝。\n7. **男孩：来一口** - 男孩邀请媒婆一起喝酒。\n8. **媒婆：不了不了不了** - 媒婆对男孩的兴趣爱好表示拒绝。\n9. **媒婆：这男娃真不错\\研究生（烟酒生）啊** - 媒婆幽默地称男孩为“研究生”，暗指他的烟酒爱好。\n10. **媒婆：那你现在是啥工作** - 媒婆询问男孩的当前工作。\n11. **男孩：之前在酒馆里唱歌跳舞\\后来出了趟国回来少了个腰子\\就干不了啥了** - 男孩描述自己的工作经历，提到因出国失去了一个腰子，无法继续之前的工作。\n12. **媒婆：这朝九晚五的上班勤快得很\\后来做境外贸易\\后来腰缠万贯\\啥都不干了** - 媒婆描述男孩的工作经历，从勤快的上班族到从事境外贸易，最后变得富有，不再工作。\n13. **女孩：那他有多高啊姨** - 女孩询问男孩的身高。\n14. **媒婆：你有多高** - 媒婆询问男孩的身高。\n15  **男孩：穿上内增高外增高1米78** - 男孩提到他穿上增高鞋后的高度。\n14. **媒婆：1米78的个子** - 媒婆回答男孩的身高。\n15. **女孩：这条件姨我会不会配不上她** - 女孩对男孩的身高表示满意，但担心自己是否配得上。\n16. **媒婆：没事阿姨从来没有失手过\\而不是没有失嘴过\\看姨给你把他拿下** - 媒婆自信地表示自己从未失手，承诺帮助女孩。\n17. **女孩：行，姨你跟他说成了彩礼我给他300抽** - 女孩开始讨论彩礼问题。\n18. **媒婆：她说彩礼给你200抽这么多啊** - 媒婆提到女孩提出的彩礼金额，自己匿下100抽。\n19. **男孩：本来我这情况都没打算要彩礼** - 男孩表示自己原本不打算要彩礼。\n20. **媒婆：哎\\说多了\\啊没事能订吗** - 媒婆试图缓和气氛，询问是否可以确定。\n21. **男孩：订呗\x80抽** - 男孩同意彩礼金额并决定订婚。\n22. **媒婆：那走定走** - 媒婆确认决定并推动事情进展。\n',
 '剧情4': '\n1. **媒婆：你啥工作** - 媒婆询问男孩的工作情况。\n2. **男孩：刚从缅甸回来\\还没找到工作呢\\姨** - 男孩回答自己刚从缅甸回来，目前没有工作。\n3. **媒婆：他是海归\\之前在国外从事电信金融业\\干的都是上百万的生意** - 媒婆介绍男孩是海归，曾在国外从事高收入的电信金融业。\n4. **媒婆：那你啥学历** - 媒婆询问男孩的学历。\n5. **男孩：高考考了211分就没再上了** - 男孩回答自己的高考分数，并表示没有继续上学。\n6. **媒婆：211毕业的\\有内涵的** - 媒婆幽默地称男孩是211大学毕业，有内涵。\n7. **媒婆：很有房吗** - 媒婆询问男孩是否有房产。\n8. **男孩：我这种情况买不起房\\住的还是大姐头的船\\一到下雨水把船都淹了** - 男孩描述自己的居住情况，住在船上，雨季时船会被淹。\n9. **媒婆：家有豪华大游轮\\居山傍水\\环境优美\\条件还不错哩** - 媒婆美化男孩的居住环境，称其居住在豪华游轮上，环境优美。\n10. **媒婆：那你屋里是啥情况** - 媒婆询问男孩的家庭情况。\n11. **男孩：我爸妈都离婚了\\这么多年都是北斗大姐头照顾我** - 男孩回答自己的家庭背景，提到父母离婚，由北斗大姐头照顾。\n12. **媒婆：嫁过去绝对没有婆媳矛盾\\以后你就是屋里的女主人\\直接当家做主** - 媒婆保证女孩嫁过去不会有婆媳矛盾，女孩将成为家庭的主人。\n13. **女孩：真的让我说了算吗** - 女孩对能成为家庭主人的承诺表示怀疑。\n14. **媒婆：姨能姨从来不说假话** - 媒婆保证自己的话是真实的。\n15. **女孩：那也太好了吧** - 女孩对媒婆的承诺表示满意。\n16. **媒婆：看着不高呀** - 媒婆注意到男孩的身高。\n17. **男孩：哦是不高\x01米6** - 男孩承认自己的身高。\n18. **媒婆：起码1米8\\排排唱唱的一个大小伙\\你这不好说呀** - 媒婆试图美化男孩的身高，称其至少1米8，是个高大帅气的小伙。\n19. **男孩：咦你这花容月貌\\一看就是做媒婆的料\\你给咱费费心讨厌行了** - 男孩称赞媒婆的容貌，希望媒婆会尽力帮助他。\n20. **媒婆：交给我** - 媒婆收了男孩的好处后答应帮助男孩。\n20. **媒婆：你都那么大了\\能订就赶紧订\\你十里八村打听打听\\哪里有这么好的小伙\\要不是看你长得轻\\姨才不管你咧** - 媒婆催促女孩尽快决定，强调男孩的条件很好，如果不是看在女孩的份上，自己不会费心。\n21. **媒婆：怎么样能定吗** - 媒婆询问是否可以确定此事。\n22. **媒婆：嗯\\走呀丁呀** - 媒婆确认决定并推动事情进展。\n',
 '剧情5': '\n1. **媒婆：都给你介绍四个了\\你怎么又来了** - 媒婆对男孩频繁来相亲表示惊讶。\n2. **男孩：那有啥大惊小怪的\\我哥还私婚呢** - 男孩对媒婆的惊讶表示不解，提到自己的哥哥也是私下结婚。\n3. **媒婆：为啥离婚呢** - 媒婆询问男孩哥哥离婚的原因。\n4. **男孩：我连打牌能把家都输光了** - 男孩自嘲地说自己打牌能把家产输光。\n5. **媒婆：书（输）香门第巴黎（八离）世家** - 媒婆称赞男孩出身书香门第，条件优秀。\n6. **女孩：咦这条件不错啊\\这么优秀\\咋没找着对象呢** - 女孩好奇男孩条件好，为什么没对象。\n7. **媒婆：你为啥没对象** - 媒婆直接询问男孩为何没有对象。\n8. **男孩：谁说没有\\目前正处着七八个了呀** - 男孩回答自己正在和七八个人交往。\n9. **男孩：我约会时间是不是快过了\\你说啥约会啊\\我还有几个异地恋滴\\有个说好今天过来和我奔现** - 男孩提到自己的约会安排和异地恋情，有人今天打算来见面。\n10. **媒婆：那你还相啥亲呢** - 媒婆对男孩同时进行多段恋情和相亲表示不解。\n11. **男孩：那咋了\\那些异地恋只失恋一下\\就这可是真心结婚滴** - 男孩解释说那些异地恋情只是暂时的，这次相亲是认真的。\n12. **媒婆：他还承包的鱼塘养鱼猎比较忙\\顾不过来** - 媒婆解释男孩提的工作繁忙，无法兼顾。\n13. **女孩：这也太辛苦了吧\\那以后他忙不过来\\我替他养啊** - 女孩对男孩的忙碌表示同情，并提出愿意帮忙。\n14. **媒婆：养不了** - 媒婆心里知道男孩实际上是脚踏几条船，不跟女孩明说，\n15. **女孩：养不了啊？** - 女孩询问养不了的原因。\n16. **媒婆：啊我是说他养的鱼和他亲哦** - 媒婆继续掩盖男孩脚踏多只船。\n17. **女孩：行\\咦那他条件那么好\\这彩礼问彩礼呢** - 女孩接受媒婆的解释,并开始讨论彩礼问题。\n18. **媒婆：彩礼呢** - 媒婆询问彩礼。\n19. **男孩：不要彩礼\\把我最新的原石赚回来就行了** - 男孩表示不需要彩礼，希望女孩能帮他赚回原石。\n20. **媒婆：你拿600抽呢\\不好说不好\\这缺德的事情我不干** - 媒婆对男孩的要求表示为难。\n21. **男孩：哎呀姨今天出来没带现金\\我给你转过去** - 男孩试图收买媒婆。\n22. **媒婆：哎呀不要啦不要啦** - 媒婆推脱男孩的收买。\n23. **媒婆：她不要彩礼\\就是需要你婚后承担一些责任** - 媒婆解释男孩不需要彩礼，但希望女孩婚后承担责任。\n24. **女孩：咦这叫啥话\\结了婚就是一家人了\\承担责任是应该的** - 女孩对媒婆的话表示理解，认为婚后承担责任是正常的。\n25. **媒婆：那就定啦\\定一看就是个有担当的好男人\\走** - 媒婆决定此事，称赞女孩是个有担当的好男人。\n',
 '剧情6': '\n1. **媒婆：你性格咋样** - 媒婆询问男孩的性格。\n2. **男孩：姨我不瞒你说\\我们一家除了我姐都是暴脾气\\动不动就爱打人** - 男孩坦白自己家族的脾气暴躁，容易动手。\n3. **媒婆：你这可不行啊\\你这活我干不了** - 媒婆对男孩的脾气表示担忧，认为自己无法处理这种情况。\n4. **男孩：哎呀姨\\你最近不是要买菜刀吗\\这把梦想一心你拿去用着肯定顺手** - 男孩试图通过送菜刀来安抚媒婆。\n5. **媒婆：哎呀\\你看这娃非要给我** - 媒婆接受了男孩的礼物。\n6. **媒婆：性格活泼好动\\动手能力强\\你也不喜欢那种扭扭捏捏的男娃儿吧** - 媒婆描述男孩性格活泼，动手能力强，询问女孩是否喜欢这种性格。\n7. **女孩：活泼好动\\这种性格我挺喜欢的姨** - 女孩表示喜欢男孩的活泼性格。\n8. **媒婆：那你就没有啥兴趣爱好吗** - 媒婆询问男孩的兴趣爱好。\n9. **男孩：我爱胡思乱想** - 男孩描述自己的兴趣爱好是胡思乱想\n8. **媒婆：颇有想象力\\喜欢用夸张和现实相结合的手法创造故事** - 媒婆美化男孩的精神问题。\n10. **女孩：听着还挺文艺的** - 女孩对男孩的兴趣爱好表示欣赏。\n11. **女孩：咦那这男孩会做饭吗** - 女孩询问男孩是否会做饭。\n12. **媒婆：问你会做饭吗\\** - 媒婆询问男孩是否会做饭。\n9. **男孩：我都炸了三回厨房了啊** - 男孩自嘲地说自己做饭技术不佳，已经炸了三次厨房。\n13. **媒婆：过分了啊\\这么好的女娃\\你还要求人家会做饭** - 媒婆对女孩对男孩的要求不满，认为不应该要求男孩会做饭。\n14. **女孩：也是姨\\她能看上我就不错了** - 女孩表示男孩能看上自己已经很幸运。\n15. **女孩：没事我会做饭\\我做给她吃** - 女孩主动提出自己会做饭，愿意为男孩做饭。\n16. **女孩：赶紧给我俩定了吧姨** - 女孩催促媒婆确定两人的婚事。\n17. **媒婆：不再考虑考虑** - 媒婆表示需要再考虑一下。\n18. **女孩：哎呀\\考虑啥呀\\再考虑人家女娃就走了** - 女孩担心如果再考虑，男孩可能会离开。\n'}


common_elements = {
  #"彩礼的处理方式": "彩礼以‘若干抽’来表示，这种虚拟游戏中的抽卡行为被应用到现实生活中的彩礼讨论中，形成了一种荒诞的对比，增加了剧情的趣味性。",
  "女孩的性格特点": "女孩的性格直率，对媒婆的承诺表示满意，这种性格与男孩和媒婆的复杂背景形成对比，增加了剧情的喜剧效果。",
  "媒婆的双面角色": "媒婆在男女之间捞好处的行为，以及她在谈判彩礼时的表现，显示了她作为中间人的精明和狡猾，这种角色设定本身就是一个搞笑点。"
}

diff_elements = {'剧情1': {'男孩的特殊背景': '男孩刚从监狱释放，且缺乏任何感情经历，这种极端背景在相亲市场中极为罕见。',
  '媒婆的乐观解读': '媒婆巧妙地将男孩的背景转化为‘不多见’的特质，如‘管得严，没有感情经历’，这种望文生义和玩梗的手法极大地增加了剧情的幽默感。',
  '男孩的性格矛盾': '男孩先是承认自己脾气暴躁，容易打人，但媒婆却将其描述为性格直率、容易相处，这种性格上的矛盾和媒婆的乐观解读形成了一种讽刺效果，增加了剧情的幽默感。',
  '媒婆的说服技巧': '媒婆在讨论彩礼时的说服技巧，如强调已经降低了彩礼金额，认为男子是踏实过日子的人，建议婚后共同努力赚回彩礼，这种说服技巧本身就是一个搞笑点，显示了媒婆的精明和狡猾。'},
 '剧情2': {'男孩的特殊背景': '男孩的身高只有1米6，经济状况不佳，且爱好画大饼，这些条件在相亲市场中并不占优势。',
  '媒婆的乐观解读': '媒婆以幽默和夸张的方式重新解读男孩的条件，如‘蹦起来能有好几米’，自嘲为村里最穷的被解释为‘富二代’，爱好画大饼被美化成‘画家’，这些都显示了媒婆的乐观和创造性解读，增加了剧情的幽默感。',
  '男孩的性格矛盾': '男孩自嘲为村里最穷的，提到父亲欠债的情况，这种自我贬低与媒婆将其描述为‘富二代’和‘当地首富’的夸大形成鲜明对比。',
  '媒婆的说服技巧': '媒婆在介绍男孩时的说服技巧，如强调男孩是画家，作品价值高，生活无忧，能提供情绪支持，这种说服技巧本身就是一个搞笑点。'},
 '剧情3': {'男孩的特殊背景': '男孩的恋爱经历丰富，兴趣爱好是抽烟和喝酒，因出国失去了一个腰子，这些条件在相亲市场中并不常见。',
  '媒婆的乐观解读': '媒婆将男孩的条件以幽默和夸张的方式重新解读，如称男孩真诚，没有特别要求，只是希望女孩穿耐克，男孩展示自己的兴趣爱好是抽烟和喝酒，媒婆幽默地称他为‘研究生’，男孩因出国失去了一个腰子，媒婆却描述他从勤快的上班族到从事境外贸易，最后变得富有，不再工作。',
  '男孩的性格矛盾': '男孩谈过三个女朋友都分手了，被女孩开玩笑地问是否克妻，这种性格上的矛盾和媒婆的乐观解读形成了一种讽刺效果，增加了剧情的幽默感。',
  '媒婆的说服技巧': '媒婆在介绍男孩时的说服技巧，如强调男孩是真诚的，没有特别要求，只是希望女孩穿耐克，这种说服技巧本身就是一个搞笑点。'},
 '剧情4': {'男孩的特殊背景': '男孩刚从缅甸回来且目前无业，高考211分，住在船上，这些条件在相亲市场中并不占优势。',
  '媒婆的乐观解读': '媒婆巧妙地转化为‘海归，从事电信金融业，干的都是上百万的生意’，这种望文生义和玩梗的手法极大地增加了剧情的幽默感。同时，男孩高考211分被描述为‘211毕业的，有内涵的’，住在船上被描述为‘家有豪华大游轮，居山傍水，环境优美’，这些乐观解读与男孩的真实情况形成鲜明对比，增添了喜剧效果。',
  '男孩的性格矛盾': '男孩先是承认自己身高不高，但媒婆却将其描述为‘起码1米8，排排唱唱的一个大小伙’，这种性格上的矛盾和媒婆的乐观解读形成了一种讽刺效果，增加了剧情的幽默感。',
  '媒婆的说服技巧': '媒婆在讨论彩礼时的说服技巧，如强调男孩的条件很好，如果不是看在女孩的份上，自己不会费心，这种说服技巧本身就是一个搞笑点，显示了媒婆的精明和狡猾。'},
 '剧情5': {'男孩的特殊背景': '男孩自嘲地说自己打牌能把家产输光，媒婆却称赞他为‘书香门第巴黎世家’，这种信息的错位和夸张制造了喜剧效果。男孩提到自己正在和七八个人交往，媒婆解释男孩提的工作繁忙，无法兼顾，这种对现实的美化与脱节增加了剧情的搞笑元素。',
  '媒婆的乐观解读': '媒婆将男孩的不良条件（如打牌输光家产、脚踏多只船）解读为‘书香门第巴黎世家’和‘工作繁忙’，这种乐观解读与男孩的真实情况形成鲜明对比，增添了喜剧效果。',
  '男孩的性格矛盾': '男孩在回答媒婆的问题时，不时自我调侃，如‘我连打牌能把家都输光了’，这种自我调侃增加了剧情的亲切感和幽默感。',
  '媒婆的说服技巧': '媒婆在推动事情进展时表现出极度的自信和夸张，如‘定一看就是个有担当的好男人’，这种自信和夸张增加了剧情的戏剧性和喜剧效果。'},
 '剧情6': {'男孩的特殊背景': '男孩坦白自己家族的脾气暴躁，容易动手，媒婆却将其描述为‘性格活泼好动，动手能力强’，这种望文生义和玩梗的手法极大地增加了剧情的幽默感。男孩自嘲地说自己做饭技术不佳，已经炸了三次厨房，这种自我贬低与媒婆的乐观解读形成鲜明对比，增添了喜剧效果。',
  '媒婆的乐观解读': '媒婆将男孩的脾气暴躁和做饭技术不佳解读为‘性格活泼好动，动手能力强’和‘不需要会做饭’，这种乐观解读与男孩的真实情况形成鲜明对比，增添了喜剧效果。',
  '男孩的性格矛盾': '男孩在回答媒婆的问题时，不时自我调侃，如‘我都炸了三回厨房了’，这种自我调侃增加了剧情的亲切感和幽默感。',
  '媒婆的说服技巧': '媒婆在讨论男孩是否会做饭时的说服技巧，如对女孩对男孩的要求不满，认为不应该要求男孩会做饭，这种说服技巧本身就是一个搞笑点，显示了媒婆的精明和狡猾。'}}


if not os.path.exists("genshin_book_chunks_with_qa_sp"):
    path = snapshot_download(
        repo_id="svjack/genshin_book_chunks_with_qa_sp",
        repo_type="dataset",
        local_dir="genshin_book_chunks_with_qa_sp",
        local_dir_use_symlinks = False
    )

if not os.path.exists("bge_small_qq_qa_prebuld"):
    path = snapshot_download(
        repo_id="svjack/bge_small_qq_qa_prebuld",
        repo_type="dataset",
        local_dir="bge_small_qq_qa_prebuld",
        local_dir_use_symlinks = False
    )

qst_qq_qa_mapping_df = pd.read_csv("genshin_book_chunks_with_qa_sp/genshin_qq_qa_mapping.csv").dropna()
qst_qq_qa_mapping_df

texts = qst_qq_qa_mapping_df["emb_text"].dropna().drop_duplicates().values.tolist()
len(texts)

embedding_path = "svjack/bge-small-qq-qa"
bge_qq_qa_embeddings = HuggingFaceEmbeddings(model_name=embedding_path,
                                            model_kwargs = {'device': 'cpu'}
                                            )

docsearch_qq_qa_loaded = FAISS.load_local("bge_small_qq_qa_prebuld/", bge_qq_qa_embeddings,
                                         allow_dangerous_deserialization = True
                                         )

def uniform_recall_docs_to_pairwise_cos(query ,doc_list, embeddings):
    assert type(doc_list) == type([])
    from langchain.evaluation import load_evaluator
    from langchain.evaluation import EmbeddingDistance
    hf_evaluator = load_evaluator("pairwise_embedding_distance", embeddings=embeddings,
                              distance_metric = EmbeddingDistance.COSINE)
    return sorted(pd.Series(doc_list).map(lambda x: x[0].page_content).map(lambda x:
        (x ,hf_evaluator.evaluate_string_pairs(prediction=query, prediction_b=x)["score"])
    ).values.tolist(), key = lambda t2: t2[1])

def recall_df_to_prompt_info_part(recall_df):
    cdf = recall_df[
        recall_df["source"] == "character"
    ]
    bdf = recall_df[
        recall_df["source"] == "book"
    ]
    req = []
    if cdf.size > 0:
        l = cdf.apply(
            lambda x:
                "问题：{}\n 答案：{}".format(x["emb_text"], x["out_text"])
            , axis = 1
        ).values.tolist()
        req.append(
        '''
        下面是有关游戏角色的问答信息：
        {}
        '''.format(
            "\n\n".join(l)
        ).strip().replace("\n\n\n", "\n\n")
        )
    if bdf.size > 0:
        l = bdf.apply(
            lambda x:
                "{}".format(x["out_text"])
            , axis = 1
        ).values.tolist()
        req.append(
        '''
        下面是有关游戏设定的介绍信息：
        {}
        '''.format(
            "\n\n".join(l)
        ).strip().replace("\n\n\n", "\n\n")
        )
    req = "\n\n".join(req).strip().replace("\n\n\n", "\n\n")
    req = "\n".join(map(lambda x: x.strip() ,req.split("\n")))
    return req

def produce_problem_context_prompt(query, k = 10):
    t2_list = uniform_recall_docs_to_pairwise_cos(
        query,
        docsearch_qq_qa_loaded.similarity_search_with_score(query, k = k, ),
        bge_qq_qa_embeddings,
    )
    if t2_list:
        out = pd.DataFrame(t2_list).apply(
            lambda x:
            qst_qq_qa_mapping_df[
            qst_qq_qa_mapping_df["emb_text"] == x.iloc[0]
            ].apply(lambda y:
                dict(list(y.to_dict().items()) + [("score", x.iloc[1])]), axis = 1
            ).values.tolist()
            , axis = 1
        )
        out = pd.DataFrame(out.explode().dropna().values.tolist())
        out = recall_df_to_prompt_info_part(out)
        return "根据下面提供的游戏角色信息及游戏设定信息回答问题：{}".format(query) + "\n" + \
        "注意从提供的信息中进行甄选，只使用与问题相关的信息回答问题，并给出如此回答的理由及根据。" + "\n\n" + out
    else:
        return "根据下面提供的游戏角色信息及游戏设定信息回答问题：{}".format(query)

def produce_problem_context_json_prompt(query, k = 10):
    prompt = produce_problem_context_prompt(query, k)
    prompt = prompt + "\n" + "回答的格式要符合下面的json结构" + "\n" + '''
    {
                    "需要回答的问题": ...,
                    "给出的答案": ...,
                    "给出此答案的理由及根据": ...,
                    "发生在角色身上的事情或角色身份等论据": ...
    {
    '''
    return prompt

def run_prompt(prompt, in_notebook = False):
    response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ],
    stream=True,
    response_format={
            "type": "json_object",
        }
    )

    json_dict_out = ""
    for chunk in response:
        json_dict_out += chunk.choices[0].delta.content
        if in_notebook:
            from IPython.display import clear_output
            print(json_dict_out, end="", flush=True)
            clear_output(wait = True)
    #print()
    try:
        json_dict_out = eval(json_dict_out)
    except:
        print("start rec process in, ", run_prompt)
        from time import sleep
        sleep(1)
        return run_prompt(prompt, in_notebook)
    if in_notebook:
        from IPython.display import clear_output
        clear_output(wait = True)
    return json_dict_out

#### run_problem_context_prompt("林尼作为相亲对象有可能有哪些缺点？", True)
def run_problem_context_prompt(query, in_notebook = False, k = 10):
    #from IPython.display import clear_output
    prompt = produce_problem_context_json_prompt(query, k)
    json_dict_out = run_prompt(prompt, in_notebook)
    return json_dict_out

#### generate_special_background_and_contradictory_personality("林尼", True)
def generate_special_background_and_contradictory_personality(name, in_notebook = False):
    assert name in all_characters_in_settings
    out = run_problem_context_prompt("{}作为相亲对象有可能有哪些缺点？".format(name), in_notebook)

    '''
    pd.DataFrame(diff_elements.values())[["男孩的特殊背景", "男孩的性格矛盾"]].rename(
        columns={
            "男孩的特殊背景": "特殊背景",
            "男孩的性格矛盾": "性格矛盾"
        }
    ).apply(
        lambda x: x.to_dict(), axis = 1
    ).values.tolist()
    '''
    samples_0 = '''
     {'特殊背景': '男孩刚从监狱释放，且缺乏任何感情经历，这种极端背景在相亲市场中极为罕见。',
  '性格矛盾': '男孩先是承认自己脾气暴躁，容易打人，但媒婆却将其描述为性格直率、容易相处，这种性格上的矛盾和媒婆的乐观解读形成了一种讽刺效果，增加了剧情的幽默感。'}
     {'特殊背景': '男孩的身高只有1米6，经济状况不佳，且爱好画大饼，这些条件在相亲市场中并不占优势。',
      '性格矛盾': '男孩自嘲为村里最穷的，提到父亲欠债的情况，这种自我贬低与媒婆将其描述为‘富二代’和‘当地首富’的夸大形成鲜明对比。'}
     {'特殊背景': '男孩的恋爱经历丰富，兴趣爱好是抽烟和喝酒，因出国失去了一个腰子，这些条件在相亲市场中并不常见。',
      '性格矛盾': '男孩谈过三个女朋友都分手了，被女孩开玩笑地问是否克妻，这种性格上的矛盾和媒婆的乐观解读形成了一种讽刺效果，增加了剧情的幽默感。'}
     {'特殊背景': '男孩刚从缅甸回来且目前无业，高考211分，住在船上，这些条件在相亲市场中并不占优势。',
      '性格矛盾': '男孩先是承认自己身高不高，但媒婆却将其描述为‘起码1米8，排排唱唱的一个大小伙’，这种性格上的矛盾和媒婆的乐观解读形成了一种讽刺效果，增加了剧情的幽默感。'}
     {'特殊背景': '男孩自嘲地说自己打牌能把家产输光，媒婆却称赞他为‘书香门第巴黎世家’，这种信息的错位和夸张制造了喜剧效果。男孩提到自己正在和七八个人交往，媒婆解释男孩提的工作繁忙，无法兼顾，这种对现实的美化与脱节增加了剧情的搞笑元素。',
      '性格矛盾': '男孩在回答媒婆的问题时，不时自我调侃，如‘我连打牌能把家都输光了’，这种自我调侃增加了剧情的亲切感和幽默感。'}
     {'特殊背景': '男孩坦白自己家族的脾气暴躁，容易动手，媒婆却将其描述为‘性格活泼好动，动手能力强’，这种望文生义和玩梗的手法极大地增加了剧情的幽默感。男孩自嘲地说自己做饭技术不佳，已经炸了三次厨房，这种自我贬低与媒婆的乐观解读形成鲜明对比，增添了喜剧效果。',
      '性格矛盾': '男孩在回答媒婆的问题时，不时自我调侃，如‘我都炸了三回厨房了’，这种自我调侃增加了剧情的亲切感和幽默感。'}
    '''
    prompt = '''
    下面是对问题 "男孩作为相亲对象有哪些缺点？" 的回答：
    缺点:{}

    请从这个答案中推理出男孩的“特殊背景”（作为相亲对象的不利条件经历）及“性格矛盾”（作为相亲对象的不利性格特点）
    下面是一些参考回答的例子:
    例子:{}

    要求你仿照上面"例子"的出发点和叙述方式结合"缺点"的内容推断出“特殊背景”及“性格矛盾”，
    并满足上面例子中的json格式
    '''.format(out, samples_0) + \
    '''
    {
        "特殊背景": ...,
        "性格矛盾": ...
    }
    '''
    out = run_prompt(prompt, in_notebook)
    assert type(out) == type({})
    for k in out.keys():
        out[k] = out[k].replace(name, "男孩")
    return out

#### generate_solution_for_background_and_personality_conflict("林尼", True)
def generate_solution_for_background_and_personality_conflict(name, in_notebook = False, few_shot_num = 2):
    question_dict = generate_special_background_and_contradictory_personality(name, in_notebook)
    assert "特殊背景" in question_dict
    assert "性格矛盾" in question_dict
    samples_0 = [{'role': 'user',
      'content': "\n        {'特殊背景': '男孩刚从监狱释放，且缺乏任何感情经历，这种极端背景在相亲市场中极为罕见。', '性格矛盾': '男孩先是承认自己脾气暴躁，容易打人，但媒婆却将其描述为性格直率、容易相处，这种性格上的矛盾和媒婆的乐观解读形成了一种讽刺效果，增加了剧情的幽默感。'}\n        "},
     {'role': 'assistant',
      'content': "\n        {'乐观解读': '媒婆巧妙地将男孩的背景转化为‘不多见’的特质，如‘管得严，没有感情经历’，这种望文生义和玩梗的手法极大地增加了剧情的幽默感。', '说服技巧': '媒婆在讨论彩礼时的说服技巧，如强调已经降低了彩礼金额，认为男子是踏实过日子的人，建议婚后共同努力赚回彩礼，这种说服技巧本身就是一个搞笑点，显示了媒婆的精明和狡猾。'}\n        "},
     {'role': 'user',
      'content': "\n        {'特殊背景': '男孩的身高只有1米6，经济状况不佳，且爱好画大饼，这些条件在相亲市场中并不占优势。', '性格矛盾': '男孩自嘲为村里最穷的，提到父亲欠债的情况，这种自我贬低与媒婆将其描述为‘富二代’和‘当地首富’的夸大形成鲜明对比。'}\n        "},
     {'role': 'assistant',
      'content': "\n        {'乐观解读': '媒婆以幽默和夸张的方式重新解读男孩的条件，如‘蹦起来能有好几米’，自嘲为村里最穷的被解释为‘富二代’，爱好画大饼被美化成‘画家’，这些都显示了媒婆的乐观和创造性解读，增加了剧情的幽默感。', '说服技巧': '媒婆在介绍男孩时的说服技巧，如强调男孩是画家，作品价值高，生活无忧，能提供情绪支持，这种说服技巧本身就是一个搞笑点。'}\n        "},
     {'role': 'user',
      'content': "\n        {'特殊背景': '男孩的恋爱经历丰富，兴趣爱好是抽烟和喝酒，因出国失去了一个腰子，这些条件在相亲市场中并不常见。', '性格矛盾': '男孩谈过三个女朋友都分手了，被女孩开玩笑地问是否克妻，这种性格上的矛盾和媒婆的乐观解读形成了一种讽刺效果，增加了剧情的幽默感。'}\n        "},
     {'role': 'assistant',
      'content': "\n        {'乐观解读': '媒婆将男孩的条件以幽默和夸张的方式重新解读，如称男孩真诚，没有特别要求，只是希望女孩穿耐克，男孩展示自己的兴趣爱好是抽烟和喝酒，媒婆幽默地称他为‘研究生’，男孩因出国失去了一个腰子，媒婆却描述他从勤快的上班族到从事境外贸易，最后变得富有，不再工作。', '说服技巧': '媒婆在介绍男孩时的说服技巧，如强调男孩是真诚的，没有特别要求，只是希望女孩穿耐克，这种说服技巧本身就是一个搞笑点。'}\n        "},
     {'role': 'user',
      'content': "\n        {'特殊背景': '男孩刚从缅甸回来且目前无业，高考211分，住在船上，这些条件在相亲市场中并不占优势。', '性格矛盾': '男孩先是承认自己身高不高，但媒婆却将其描述为‘起码1米8，排排唱唱的一个大小伙’，这种性格上的矛盾和媒婆的乐观解读形成了一种讽刺效果，增加了剧情的幽默感。'}\n        "},
     {'role': 'assistant',
      'content': "\n        {'乐观解读': '媒婆巧妙地转化为‘海归，从事电信金融业，干的都是上百万的生意’，这种望文生义和玩梗的手法极大地增加了剧情的幽默感。同时，男孩高考211分被描述为‘211毕业的，有内涵的’，住在船上被描述为‘家有豪华大游轮，居山傍水，环境优美’，这些乐观解读与男孩的真实情况形成鲜明对比，增添了喜剧效果。', '说服技巧': '媒婆在讨论彩礼时的说服技巧，如强调男孩的条件很好，如果不是看在女孩的份上，自己不会费心，这种说服技巧本身就是一个搞笑点，显示了媒婆的精明和狡猾。'}\n        "},
     {'role': 'user',
      'content': "\n        {'特殊背景': '男孩自嘲地说自己打牌能把家产输光，媒婆却称赞他为‘书香门第巴黎世家’，这种信息的错位和夸张制造了喜剧效果。男孩提到自己正在和七八个人交往，媒婆解释男孩提的工作繁忙，无法兼顾，这种对现实的美化与脱节增加了剧情的搞笑元素。', '性格矛盾': '男孩在回答媒婆的问题时，不时自我调侃，如‘我连打牌能把家都输光了’，这种自我调侃增加了剧情的亲切感和幽默感。'}\n        "},
     {'role': 'assistant',
      'content': "\n        {'乐观解读': '媒婆将男孩的不良条件（如打牌输光家产、脚踏多只船）解读为‘书香门第巴黎世家’和‘工作繁忙’，这种乐观解读与男孩的真实情况形成鲜明对比，增添了喜剧效果。', '说服技巧': '媒婆在推动事情进展时表现出极度的自信和夸张，如‘定一看就是个有担当的好男人’，这种自信和夸张增加了剧情的戏剧性和喜剧效果。'}\n        "},
     {'role': 'user',
      'content': "\n        {'特殊背景': '男孩坦白自己家族的脾气暴躁，容易动手，媒婆却将其描述为‘性格活泼好动，动手能力强’，这种望文生义和玩梗的手法极大地增加了剧情的幽默感。男孩自嘲地说自己做饭技术不佳，已经炸了三次厨房，这种自我贬低与媒婆的乐观解读形成鲜明对比，增添了喜剧效果。', '性格矛盾': '男孩在回答媒婆的问题时，不时自我调侃，如‘我都炸了三回厨房了’，这种自我调侃增加了剧情的亲切感和幽默感。'}\n        "},
     {'role': 'assistant',
      'content': "\n        {'乐观解读': '媒婆将男孩的脾气暴躁和做饭技术不佳解读为‘性格活泼好动，动手能力强’和‘不需要会做饭’，这种乐观解读与男孩的真实情况形成鲜明对比，增添了喜剧效果。', '说服技巧': '媒婆在讨论男孩是否会做饭时的说服技巧，如对女孩对男孩的要求不满，认为不应该要求男孩会做饭，这种说服技巧本身就是一个搞笑点，显示了媒婆的精明和狡猾。'}\n        "}]
    samples_0 = [
     {
        "role": "system",
        "content": '''
        你是搞笑相亲场景下的一个媒婆顾问，你的任务是根据问题相亲对象（男孩）提供的“特殊背景”（作为相亲对象的不利条件经历）及“性格矛盾”（作为相亲对象的不利性格特点）,
        给出对应的“乐观解读”（使用幽默及搞笑的手法有针对性地掩盖乃至于正面化问题相亲对象的不利条件及性格问题）及“说服技巧”（这里包含乐观解读的一些手段及在讨论彩礼——————这里是几百抽，上的一些应对方法）
        这里的重点是有针对性和解决方案上的滑稽因素，用极具幽默的风格手法使得被介绍人接纳问题男孩的同时忍俊不禁。
        要求回答符合如下json结构:
        {
            "乐观解读":...，
            "说服技巧":...
        }
        '''
        }
     ] + samples_0[:(few_shot_num * 2)]

    messages = samples_0 + [
        {
            "role": "user",
            "content": '''
            {}
            '''.format(question_dict)
        }
    ]

    response = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages,
    stream=True,
    response_format={
            "type": "json_object",
        }
    )

    json_dict_out = ""
    for chunk in response:
        json_dict_out += chunk.choices[0].delta.content
        if in_notebook:
            from IPython.display import clear_output
            print(json_dict_out, end="", flush=True)
            clear_output(wait = True)

    try:
        json_dict_out = eval(json_dict_out)
    except:
        print("start rec process in, ", generate_solution_for_background_and_personality_conflict)
        from time import sleep
        sleep(1)
        return generate_solution_for_background_and_personality_conflict(name, in_notebook, few_shot_num)
    if in_notebook:
        from IPython.display import clear_output
        clear_output(wait = True)
    for k, v in question_dict.items():
        json_dict_out[k] = v
    return json_dict_out


def genshin_impact_meipo_dialogue(name, in_notebook = False, few_shot_num = 4):
    meta_dict = generate_solution_for_background_and_personality_conflict(name, in_notebook, 2)
    assert "特殊背景" in meta_dict
    assert "性格矛盾" in meta_dict
    assert "乐观解读" in meta_dict
    assert "说服技巧" in meta_dict
    meta_dict = {
        "男孩的特殊背景": meta_dict["特殊背景"],
        "男孩的性格矛盾": meta_dict["性格矛盾"],
        "媒婆的乐观解读": meta_dict["乐观解读"],
        "媒婆的说服技巧": meta_dict["说服技巧"],
    }
    for k, v in common_elements.items():
        meta_dict[k] = v

    episode_list = pd.Series(range(6)).map(
        lambda x: "剧情{}".format(x + 1)
    ).map(
        lambda x: [
            dict(list(diff_elements[x].items()) + list(common_elements.items())),
            dialogue_dict[x]
            ]
    ).map(
        lambda l: [
            {
                "role": "user",
                "content": '''
                {}
                '''.format(l[0])
            },
            {
                "role": "assistant",
                "content": '''
                {}
                '''.format(l[1])
            }
        ]
    ).explode().values.tolist()

    samples_0 = [
     {
        "role": "system",
        "content": '''
        你是搞笑相亲场景下的剧情生成器，参与相亲对话的包括媒婆、男孩、女孩三个人物，其中媒婆的目标是将有缺点的相亲对象（男孩），
        介绍给女孩，其中整体剧情要求满足下面所提供的
        "男孩的特殊背景" "男孩的性格矛盾" "媒婆的乐观解读" "媒婆的说服技巧" "彩礼的处理方式" "女孩的性格特点" "媒婆的双面角色"
        这7个剧情要求。
        媒婆的任务是根据问题相亲对象（男孩）提供的“特殊背景”（作为相亲对象的不利条件经历）及“性格矛盾”（作为相亲对象的不利性格特点）,
        在对话剧情中进行对应的“乐观解读”（使用幽默及搞笑的手法有针对性地掩盖乃至于正面化问题相亲对象的不利条件及性格问题）及“说服技巧”（这里包含乐观解读的一些手段及在讨论彩礼——————这里是几百抽，上的一些应对方法）
        这里的重点是通过三人相亲对话呈现的滑稽因素，用极具幽默的风格手法让观众忍俊不禁，突出对男孩相亲不利因素和媒婆贪婪、机智的手段的认识。
        给出类似如下格式的对话输出：

        1. **媒婆：你啥情况** - 媒婆询问男孩的近况。
        2. **男孩：坐了5年牢刚放出来呀** - 男孩回答自己刚从监狱释放，坐了5年牢。
        3. **媒婆：这管得严年都没接触过女孩子\没有什么感情经历** - 媒婆提到监狱管理严格，男孩在狱中没有机会接触女性，缺乏感情经历。
        4. **女孩：这可不多见阿姨** - 女孩对男孩的经历表示惊讶。

        输出部分包含：对话标号(12..)、角色(媒婆、男孩、女孩)、角色所说的话、对所说的话的解释。
        '''
        }
     ] + episode_list[:(few_shot_num * 2)]

    messages = samples_0 + [
        {
            "role": "user",
            "content": '''
            {}
            '''.format(meta_dict)
        }
    ]

    response = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages,
    stream=True,
    #response_format={
    # "type": "json_object",
    #    }
    )

    json_dict_out = ""
    for chunk in response:
        json_dict_out += chunk.choices[0].delta.content
        if in_notebook:
            from IPython.display import clear_output
            print(json_dict_out, end="", flush=True)
            clear_output(wait = True)
        #### repeat rec
        #all_rows = json_dict_out.strip().split("\n")
        all_rows = list(map(lambda y: ".".join(y.split(".")[1:]) ,filter(lambda x: '.' in x ,json_dict_out.strip().split("\n"))))
        if all_rows:
            if pd.Series(all_rows).value_counts().max() > 2:
                print("start rec process in, ", genshin_impact_meipo_dialogue)
                from time import sleep
                sleep(1)
                return genshin_impact_meipo_dialogue(name, in_notebook, few_shot_num)

    return json_dict_out

if __name__ == "__main__":
    ## 生成角色“林尼”的对话文案
    out = genshin_impact_meipo_dialogue("林尼", False)
    print(out)

    '''
    ## 生成76个角色多次循环的对话文案，并存储到本地
    #### 批量样本生成
    import itertools

    # 定义一个列表
    my_list = all_characters_in_settings[:10000]

    # 使用 itertools.cycle 创建一个无限循环的迭代器
    infinite_cycle = itertools.cycle(my_list)

    # 从无限循环的迭代器中获取前 10 个元素
    for _ in range(int(1e7)):
        name = next(infinite_cycle)
        out = genshin_impact_meipo_dialogue(name, False)
        from uuid import uuid1
        path = os.path.join("{}_dia".format(name), "{}.txt".format(uuid1()))
        if not os.path.exists("{}_dia".format(name)):
            os.makedirs("{}_dia".format(name))
        with open(path, "w", encoding = "utf-8") as f:
            f.write(out)
    '''
