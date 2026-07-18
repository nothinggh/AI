def create():
    name = input("이름 입력: ")
    age = input("나이 입력: ")
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, age) VALUES (?, ?)", (name, age)
        )
        conn.commit()
    print("✨ 추가 성공!")













def main():
    while True:
        print('\n===관리 프로그램===')
        print('1.조회')
        print('2.추가')
        print('3.수정')
        print('4.삭제')
        print('0.종료')
        choice=input('선택:')

        if choice=='1':
            조회()
        elif choice=='2':
            create()
        elif choice=='3':
            수정()
        elif choice=='4':
            삭제()
        elif choice=='0':
            print('프로그램 종료.')
            break
        else:
            print('없는 항목입니다. 0~4사이의 숫자를 입력하세요.')

if __name__=='__main__': main()


    