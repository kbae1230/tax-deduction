import streamlit as st
import datetime

class 과세표준:
    def 소득공제(self, 연소득, 신용, 현금, 체크):
        공제 = 연소득*0.25
        신용_공제 = 0
        체크_현금_공제 = 0
        if 신용+체크+현금 >= 공제:
            if 신용 > 공제:
                신용_공제 = (신용-공제)*0.15
                체크_현금_공제 = (체크+현금)*0.3
            elif 신용 == 공제:
                체크_현금_공제 = (체크+현금)*0.3
            else:
                공제 -= 신용
                체크_현금_공제 = ((체크+현금)-공제)*0.3
        
        소득_공제 = 신용_공제 + 체크_현금_공제
        if 소득_공제 > 소득공제_한도액:
            소득_공제 = 소득공제_한도액
        global 추천
        추천 = {
                "신용_공제": 신용_공제,
                "체크_현금_공제": 체크_현금_공제,
                "소득_공제": 소득_공제,
            }
        return 소득_공제

    def 소득공제_초과(self):
        return 0


# 300만원까지, 연소득 상한 7000
def 급여별_총한도액(연소득):
    if 연소득 <= 7000:
        return 300
    elif 연소득 > 7000:
        return 250        


def run_options(selected_options):
    selected_options = [eval(i+'()') for i in selected_options]
    return selected_options


def result_message(차감징수액):
    차감징수액 = int(차감징수액)
    if 차감징수액 > 0:
        return f'{차감징수액}만원 지불하셔야 합니다.'
    else:
        return f'{차감징수액}만원 환급 대상입니다.' 
    
    
def 소득공제_결과(소득_공제):
    if 소득_공제 < 소득공제_한도액:
        return f"<p style='color:red'>{int(소득공제_한도액-소득_공제)}만원 공제 가능합니다.</p>"
    else:
        return f"<p style='color:green'>소득공제를 초과 달성.</p>"


def get_current_time():
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")

# 방문자 수 증가 및 현재 시간 로깅
def log_visitor():
    global visitor_count
    visitor_count += 1
    # st.markdown(f'<div class="footer1">방문자 수: {visitor_count}<br>최근 방문 시간: {get_current_time()}', unsafe_allow_html=True)
    print(f'방문자 수: {visitor_count}')
    print(f'최근 방문 시간: {get_current_time()}')
    with open(log_file_path, "a+") as log_file:
        log_file.write(f"{get_current_time()} - 방문자 수: {visitor_count}\n")

def main():
    log_visitor()

    st.title("연말정산 (소득공제)")
    col1, col2 = st.columns(2)
    
    with col1:
         # 숫자 입력 필드
        global 연소득
        연소득 = st.text_input("연소득", value='', placeholder="연소득 입력 (만원)", help="연간 근로소득에서 비과세소득(식대, 교통비, 양육비 등)을 제외한 금액입니다")
        if 연소득:
            st.write(연소득, "만원")
        신용 = st.text_input("신용카드", value='',  placeholder="사용액 입력 (만원)",help="사용액 입력")
        if 신용:
            st.write(신용, "만원")
        
        현금 = st.text_input("현금영수증", value='', placeholder="사용액 입력 (만원)", help="사용액 입력")
        if 현금:
            st.write(현금, "만원")
        else:
            현금 = 0
        
        체크 = st.text_input("체크카드", value='', placeholder="사용액 입력 (만원)", help="사용액 입력")
        if 체크:
            st.write(체크, "만원")
        else:
            체크 = 0
        
        try:
            연소득 = int(연소득)
            신용 = int(신용)
            현금 = int(현금)
            체크 = int(체크)
        except ValueError:
            신용 = 0
            현금 = 0
            체크 = 0

        if 연소득:
            button_enable = False
        else:
            button_enable = True

        button_result = st.button("계산", disabled=button_enable)

    with col2:
        # 1단계
        # 2단계
        # 3단계
        if button_result:
            global 소득공제_한도액
            소득공제_한도액 = 급여별_총한도액(연소득)
            과세 = 과세표준()
            st.markdown('<p class="title">분석결과</p>', unsafe_allow_html=True)
            소득_공제 = round(과세.소득공제(연소득, 신용, 현금, 체크))
            분석결과 = 소득공제_결과(소득_공제)
            
            st.markdown(분석결과, unsafe_allow_html=True)
            st.markdown('<p class="title">추천</p>', unsafe_allow_html=True)
            
            def compare(소득_공제, 신용, 체크_현금):
                '''
                신용공제가 충족될 때, 안될 떄
                안되면, 신용 충족 시키는 게 좋을지, 안좋을지
                '''
                if 소득_공제 == 소득공제_한도액:
                    st.markdown('<p class="highlight-result">소득공제를 모두 채우셨기 때문에, 혜택이 좋은 카드를 쓰시는 걸 추천드립니다.</p>', unsafe_allow_html=True)
                else:
                    # 신용카드 사용량이 많아서 체크현금 공제 빼고 부족 금액을 신용금액으로만 채웠을 때
                    부족_신용 = 연소득*0.25 - 신용
                    if 부족_신용 <= 0:
                        # 부족_신용만 = (소득공제_한도액 - 신용_공제 - 체크_현금_공제)/0.15
                        부족_체크_현금 = (소득공제_한도액 + 부족_신용*0.15 - 체크_현금*0.3)/0.3
                        추천_방법 = '부족_체크_현금'
                    else:
                        # 체크현금 공제 빼고 부족 금액을 신용 + 체크현금으로 채웠을 때
                        부족_체크_현금 = (소득공제_한도액 - 체크_현금*0.3)/0.3
                        
                        # 체크현금 공제 빼고 부족 금액을 체크현금으로만 채웠을 때
                        부족_신용_체크_현금 = 소득공제_한도액/0.3 + 부족_신용 - 체크_현금
                        
                        def str_values(부족_체크_현금, 부족_신용_체크_현금):
                            return locals()
                        추천_방법 = min(str_values(부족_체크_현금, 부족_신용_체크_현금))
                    
                    if 추천_방법 == '부족_체크_현금':
                        st.markdown('<p class="highlight-recommand">체크카드 및 현금을 우선적으로 사용하세요.</p>', unsafe_allow_html=True)
                        
                        col1, col2 = st.columns(2)
                        col1.metric("체크카드 & 현금영수증", f"{int(부족_체크_현금)}만원")
                        
                    elif 추천_방법 == '부족_신용_체크_현금':
                        st.markdown('<p class="highlight-recommand">신용카드를 우선적으로 사용하세요.</p>', unsafe_allow_html=True)
                        
                        col1, col2= st.columns(2)
                        col1.metric("신용카드", f"{int(부족_신용)}만원")
                        if 부족_신용_체크_현금 - 부족_신용 != 0:
                            col2.metric("체크카드 & 현금영수증", f"{int(부족_신용_체크_현금 - 부족_신용)}만원")
                    
            체크_현금 = 체크 + 현금
            compare(소득_공제, 신용, 체크_현금)
            
            
style = """
    <style>
    .title {
    font-size: 30px !important;
    font-weight: bold !important;
    }
    .highlight-text {
        background-color: rgba(0, 128, 0, 0.2) !important;
        padding: 5px;
        border-radius: 5px;
    }
    .highlight-result {
        background-color: rgba(0, 128, 0, 0.2) !important;
        padding: 5px;
        border-radius: 5px;
    }
    .highlight-recommand {
        background-color: rgba(255, 0, 0, 0.2) !important;
        padding: 5px;
        border-radius: 5px;
    }
    .footer1 {
        position: fixed;
        bottom: 0;
        left: 0;
        padding: 10px;
    }
    .footer2 {
        bottom: 0;
        right: 0;
        padding: 10px;
    }
    .stTextInput input {
    font-size: 30px !important;
    }
    .markdown-text-container {
        font-size: 30px !important;
    }
    </style>
    """            
            
if __name__ == '__main__':
    visitor_count = 0
    log_file_path = "visitor_log.txt"
    main()
    # Copyright 및 주의 사항 텍스트
    copyright_text = """

    간단한 소득공제 확인을 위한 도구일 뿐이며, 실제 결과와는 차이가 있을 수 있습니다. 
    참고로만 활용하시고 개발자는 어떠한 법적 책임도 지지 않습니다. © Copyright KBAE
    
    """

    st.markdown(style, unsafe_allow_html=True)
    st.markdown(f'<div class="footer2">{copyright_text}', unsafe_allow_html=True)
