# 일반 도메인 대화 데이터 셋 (3,000건)

## 파일 구성
- src_도메인.txt : 해당 도메인에 대한 입력 발화
- tgt_도메인.txt : 해당 도메인에 대한 응답 발화

## 파일 설명
- src_도메인.txt의 n번째 라인의 응답 발화는 tgt_도메인.txt n번째에 있음 </br>
**src_food.txt**: `207  나 지금 쇼핑 왔는데 수박이 너무 맛있어 보인다.` </br>
**tgt_food.txt**: `207  수박 맛있지 하나 사보는 게 어때?` </br>

## 도메인
- 음식(food)
- 날씨(weather)
- 쇼핑(shop)

## 데이터 통계
|-|음식|날씨|쇼핑|
|:---:|:---:|:---:|:---:|
|발화쌍의 수|1,000|1,000|1,000|
|발화 당 형태소 수|12.99|13.03|14.35|
|발화 당 어절 수|6.17|6.09|6.41|
|고유 형태소 수|2,355|2,040|2,593|
|고유 어절 수|4,906|4,641|5,491|
