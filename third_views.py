from django.shortcuts import render, get_object_or_404, redirect
from third.models import Restaurant, Review
from django.core.paginator import Paginator
from third.forms import RestaurantForm, ReviewForm, UpdateRestaurantForm
from django.http import HttpResponseRedirect
from django.db.models import Count, Avg

# Create your views here.
def list(request):
    restaurants = Restaurant.objects.all().annotate(reviews_count=Count('review')).annotate(average_point=Avg('review__point'))  # restaurants라는 인스턴스 변수에 할당함.
    paginator = Paginator(restaurants, 5)  # 한페이지당 5개씩 보여주겠다는 뜻이다. 참고로 Paginator는 import해서 사용해주어야한다.

    page = request.GET.get('page')  # 현재 보고있는 페이지가 어떤 페이지를 조회를 원했는지 url의 parameter(파라미터)에서 받아옴.
                                    # 예를들어 third/list?page=1 에서 1이 파라미터이다. 참고로 이건 패스 파라미터가 아니라 쿼리 파라미터이다.
    items = paginator.get_page(page)  # 쿼리 파라미터에서 페이지값을 받아서 그 페이지에 맞는 item들만 필터링해서 보여주겠다는 의미이다.
                                      # 즉, 쿼리 파라미터에서 받은 페이지값에 맞는 필드 정보들을 items 라는 변수에 넣었고, 그뿐만아니라 페이지 정보도 함께담겨간다. 그걸 렌더링 할 것이다.

    context = {
        'restaurants': items
    }
    return render(request, 'third/list.html', context)
# views.py 파일의 def list 메소드에서
# Restaurant 모델클래스에서 릴레이션명으로 상대 모델클래스에 접근하기위해서 'review'를 사용하게되고,
# 여기선 Count를 세는데에 당사자인 review 밖에 필요하지않기때문에 'review'만 사용한다. 물론 이번 코드의 경우지 보편적인것이 아니니 주의하자.
# restaurants = Restaurant.objects.all().annotate(reviews_count=Count('review')) 을 적어줌으로써
# annotate를 사용하였으므로,
# Restaurant 모델클래스의 'review' 릴레이션명을 불러와 그걸 Count 연산을 통해 결과값을 reviews_count 라는 속성을 만들어 그 안에 값을 할당하고,
# models.py 파일의 Restaurant 모델클래스 안에도 reviews_count 속성을 새로 추가해주게 되는것이다.
# 그러면 이제 reviews_count라는 속성으로 꺼내서 쓸 수 있게 된다.
# list.html 파일에서
# {% for item in restaurants %}
#     리뷰: {{ item.reviews_count }}개
# {% endfor %}
# 이렇게 사용하여 헤당 페이지의 특정 식당의 리뷰가 몇개인지 알려주는 코드를 적을 수 있게 된것이다.
# 이로써 annotate 메소드와 연산 메소드 사용을 통하여, aggregation을 해주게 된것이다.
# 참고로 annotate는 .annotate()로 계속 뒤에 덧붙여서 여러개를 적을 수 있다.
# 예를들어 restaurants = Restaurant.objects.all().annotate(reviews_count=Count('review')).annotate(average_point=Avg('review__point')) 이런식으로 말이다.
# 그리고 restaurants = Restaurant.objects.all().annotate(average_point=Avg('review__point')) 부분은
# 저 위의 Count 예시와는 다르게, 릴레이션명인 review 자체만 필요한것이 아닌, 리뷰평점의 평균값을 연산하여 구하고 싶은것이므로,
# Restaurant 모델클래스에서 릴레이션명인 review로 접근하여 Review 모델클래스로 접근하고, 그 속성인 point으로 접근하여야 하므로,
# review__point 를 사용하게 된것이다. 결국은 해당 식당의 리뷰들의 평점 평균점수를 구하게 되고, 그 결과값을 average_point 속성에 할당하게된것이다.
# 아마 average_point 속성도 models.py 파일의 Restaurant 모델클래스의 속성 목록에 자동으로 추가가 되었을것이다.
# 그러면 이제 average_point라는 속성으로 꺼내서 쓸 수 있게 된다.
# list.html 파일에서
# {% for item in restaurants %}
#     평점: {{ item.average_point }}점
# {% endfor %}

def create(request):
    if request.method == 'POST':
        form = RestaurantForm(request.POST)  # 'POST' 요청으로 들어온 모든 데이터를, third_forms.py 파일의 모델폼인 RestaurantForm에 담아서 바로 데이터를 저장할 수 있다. 그리고 form이라는 변수에 저장한다.
        if form.is_valid():
            new_item = form.save()  # 이제 DB에 저장
        return HttpResponseRedirect('/third/list/')  # 유효성 검사가 성공해서 DB에 저장이 되든, 실패를해서 저장이 안되던간에, /third/list/ 경로로 리다이렉트 시킴. third_urls.py 파일의 path('list/') 부분으로 넘어가면 됨.
    form = RestaurantForm()  # 만약 request.method == 'GET' 이라면, 그저 third_forms.py 파일에 적어둔 겉의 폼 양식만 가져옴.
    return render(request, 'third/create.html', {'form': form})  # form 변수의 값을 넣은 'form'이라는 이름으로 겉폼양식을 third/create.html 파일에 렌더링 시킴.
# <과정 설명 (각 과정에 설명과 해당코드를 적어둠. 설명 부분은 앞에 @라고 적어두겠음.)>
# 1. @ third_views.py 파일의 create 메소드를 첫 실행하게 됨. 그러면 아직 POST 요청이 아닌, GET 요청임. (현재 GET 방식인 상태)
# 2. @ third_forms.py 파일의 모델폼인 RestaurantForm의 겉폼양식을 가져와서, third/create.html 로 렌더링시킴. (현재 GET 방식인 상태)
#      form = RestaurantForm()
#      return render(request, 'third/create.html', {'form': form})
# 3. @ third/create.html 실행. 그러면 렌더링해온 겉폼 양식이 띄워지는데, 거기다가 값을 입력하고 제출함. (현재 GET 방식인 상태)
# 4. @ third/create.html 파일에 적힌 <form action="{% url 'restaurant-create' %}" method="post">로 인하여 방식이 POST로 변환되며 입력값이 third_urls.py 파일의 name='restaurant-create'인 부분에 적힌 third_views.py 파일의 create 메소드로 값을 보내줌. (현재 POST 방식인 상태)
# 5. @ 그러면 third_views.py 파일의 if request.method == 'POST': 부분의 조건을 만족시키게 되고, 해당 if 조건 부분 내용 실행.
#    if request.method == 'POST':
# 6. @ POST 요청으로 들어온 모든 데이터를, third_forms.py 파일의 모델폼인 RestaurantForm의 fields 목록의 'name', 'address' 안에 입력값을 담고, 모델에 데이터를 임시 저장한다. 그리고 그렇게 저장된 모델폼 클래스인 RestaurantForm의 정보를 form이라는 변수를 선언하여 그 변수 안에 할당한다.
#      form = RestaurantForm(request.POST)
# 7. @ 그렇게 할당된 form 변수 안의 데이터에 대하여 유효성 검사(예를들어 글자수가 맞게 입력되었는지 등)를 하게됨.
#      if form.is_valid():
# 8. @ 유효성 검사에 성공하였다면, 모델폼에 임시저장하였던 fields 들의 데이터를, 할당한 form 변수를 통하여 실제로 완전히 DB에 저장시킴.
#      new_item = form.save()
# 9. @ 유효성 검사가 성공해서 DB에 저장이 되든, 실패를해서 저장이 안되던간에, /third/list/ 경로로 리다이렉트 시킴. 이는 third_urls.py 파일의 path('list/') 부분으로 넘어가면 됨. 그러면 결국은 views.list로 인하여 third_views.py 파일의 list 메소드 실행됨.
#      return HttpResponseRedirect('/third/list/')
# 10. @ 결국은 위의 과정9까지의 진행 결과로 저장된 DB를, list 메소드에서 사용하게 되는 것이다. 이처럼 라우팅을 통하여, 모델폼을 이용한 입력값을 DB에 저장하는 과정이 완료된 것이다.
# @ 즉, 밑의 4가지 파일과 urls.py 파일로 DB 저장 및 폼 라우팅이 이루어진다.
# @ models.py 파일에서는 텍스트의 유효 최대크기 같은거랑 created_at이랑 updated_at만 코드로 적어두고,
# @ forms.py 파일에서는  모델폼으로 그 겉폼틀의 코드를 작성하면 되고,
# @ views.py에서는 렌더링 코드를 작성하면 되고,
# @ html 파일에서는 <form action="{% url 'restaurant-create' %}" method="post">와 {% csrf_token %}와 <table>{{ form.as_table }}</table> 코드를 활용하여 코드를 완성하면 된다.

def update(request):  # 리퀘스트와 데이터베이스를 직접 활용해서 업데이트하는 메소드
    # 중요한점은, create 메소드는 그저 html파일에서 post로 제출한 그 값 그대로 갖고와서 form = RestaurantForm(request.POST) 처럼 새로 모델인스턴스를 만들어서 데이터베이스에 저장해주는게 끝이지만,
    # 그러나 update 메소드는 기존 데이터베이스에 있던 인스턴스를 가져와서 그걸 참고하여 리퀘스트값을 다시 갱신을 해주는 것이기때문에 과정이 다르다.
    # 이외의 부가 설명은: https://blossoming-man.tistory.com/entry/CRUD%EB%A5%BC-%EC%9C%84%ED%95%9C-ModelForm
    if request.method == 'POST' and 'id' in request.POST:  # id값 없이 POST로 온 데이터가 있다면 그건 잘못 온 데이터이니까 'id' in request.POST 도 적어줘야 한다.
        # item = Restaurant.objects.get(pk=request.POST.get('id'))  # 참고로 request.POST.get('id') 가 한묶음이다.
        item = get_object_or_404(Restaurant, pk=request.POST.get('id'))  # id값이 없는 데이터라 로딩안될때 사이트에 에러 안뜨고 'Page not found (404)'이라는 화면만 뜨고, 에러 내용이 뜨지 않는다. 참고로 shortcuts도 사용했다.
        password = request.POST.get('password', '')  # 수정된 데이터가 POST방식으로 update메소드로 전달되어왔고, 그 데이터는 models.py 파일의 Restaurant 모델클래스의 정보이다. 그렇기때문에 괄호안의 'password'는 수정할때 새로 입력받은 Restaurant 모델클래스의 'password'필드를 의미한다.
                                                     # 그 새로수정하여 입력받은 'password' 필드 값이 정상적으로 request.POST 전달이 되어왔다면 수정한 'password'필드의 value 값을 password 변수에 할당하고,
                                                     # 그 'password' 필드 값이 정상적으로 전달되어오지 않았다면, 빈 문자열인 ''값이 password 변수에 할당되는 것이다.
        form = UpdateRestaurantForm(request.POST, instance=item)  # 어차피 UpdateRestaurantForm 모델폼클래스도 model = Restaurant 라서, RestaurantForm 모델폼클래스와 마찬가지로 리퀘스트로 받아온 게시물 수정 필드값을 그대로 저장해줄 수 있음.
        if form.is_valid() and password == item.password:  # and 이후의 코드는, 입력한 패스워드 DB의 패스워드와 일치하는지 검증하는 코드이다.
            item = form.save()
    elif request.method == 'GET':
        # item = Restaurant.objects.get(pk=request.GET.get('id'))  # update.html 파일의 {{ form.instance.id }} 코드 부분과 연계된다.
        item = get_object_or_404(Restaurant, pk=request.GET.get('id'))  # id값이 없는 데이터라 로딩안될때 사이트에 에러 안뜨고 'Page not found (404)'이라는 화면만 뜨고, 에러 내용이 뜨지 않는다. 참고로 shortcuts도 사용했다.
        form = RestaurantForm(instance=item)  # update.html 파일의 {{ form.instance.id }} 코드 부분과 연계된다.
        return render(request, 'third/update.html', {'form': form})
    return HttpResponseRedirect('/third/list/')  # if와 elif 둘다 해당되지 않을때 url path를 '/third/list/'로 리다이렉트 시켜서, 리스트 화면으로 이동한다.
# instance=item의 의미가 '참고하다'의 의미가 아닌, '수정될 데이터베이스의 모델 인스턴스' 라는 의미로 생각하면 훨씬 코드를 이해하기 쉽고, 그리고 이론적으로도 이게 더 정확한 표현이다.
# 이러한 의미로 전체적인 과정을 쉽고 간단하게 요약해서 설명하자면,
# <elif GET 부분> (아마 내 개인적인 생각 및 추측으로는, 가장 먼저 발생하는 일은 list.html 파일에서 데이터 목록중 하나를 골라 수정하기 버튼을 누르면 그 데이터의 id값이 쿼리 파라미터로 보내져서 GET방식이 되고, 그 id값에 맞는 겉폼형식이 나타나는 과정이 아닐까 싶다.)
#   사용자가 쿼리 파라미터 id값을 지닌 url 사이트로 접속을 하면, 그 id값이 사이트 쿼리파라미터로 GET으로 보내지고,
#   그렇게 쿼리파라미터로 받은 데이터의 id값과 동일한 pk id값의 데이터베이스의 모델 인스턴스를 item 변수에 넣어주고,
#   form = RestaurantForm(instance=item) 안에 request.POST 매개변수가 없으므로, 그저 지정한 id의 item의 겉폼양식을 갖고와서 form 변수에 저장해준다.
#   그렇게 해당 id의 겉폼 양식을 update.html 파일로 렌더링 해준다.
# <라우팅을 통해 method=GET에서 POST로 전환>
#   이렇게, id에 맞는 수정 겉폼 양식이 불려와진 update.html 에서 수정을 완료하고 제출하면, 그게 POST방식으로 리퀘스트 값을 가지고 urls.py 파일을 거쳐서 views.py 파일의 update 메소드로 와서 if POST 부분을 실행하게 되는 과정이 된다.
# <if POST 부분>
#   예를들어 불러와진 수정 겉폼양식에서 id=2 쿼리 파라미터의 모델 인스턴스의 데이터 필드의 name과 address 부분의 내용을 수정하여, name='바뀐거'과 address='바뀐거'으로 수정하여 제출을 눌렀다면,
#   모델 인스턴스 데이터인 {id=2, name='원래꺼', address='원래꺼}가 아닌, {id=2, name='바뀐거', address='바뀐거'}가 request.POST 로 새로 입력한 모델 인스턴스가 리퀘스트값으로 보내진다.
#   그렇게 리퀘스트값의 id=2과 동일한 id의 모델 인스턴스를 데이터베이스에서 가져와 item 변수에 넣어준다.
#   그러면 이제 form = RestaurantForm(request.POST, instance=item) 코드의 의미는,
#   수정 대상은 instance=item 이고 새로운 데이터는 request.POST 이므로, id=2인 데이터베이스의 모델 인스턴스를 {id=2, name='바뀐거', address='바뀐거'}로 바꿔주고, 그 바뀐정보를 form 변수에 넣어준다는 의미이다.
#   하여튼 그렇게해서 form 변수에 저장된 모델 인스턴스 정보 값을 유효성 검사를 하고 통과하면 form.save()로 임시가 아닌 완전히 데이터베이스에 값을 저장함으로써, 데이터베이스의 item을 {id=2, name='바뀐거', address='바뀐거'}으로 갱신하여 업데이트가 된것이다.
# ====================== // 이 밑의 설명은 초반에 잘못적은 약간 틀린 정리 요약이다. 혹시 쓸데가 있을지 몰라 삭제하지않고 남겨둘테니 주의하자. // ======================
# 우선 가장 헷갈리는 instance=item의 의미부터 설명하자면, "item 모델 인스턴스의 겉껍떼기 필드 등등의 양식만 참고하겠다." 라는 의미이다.
# 만약에 id값이 4로 부여된 item의 instance=item 라면, "pk=4에 해당하는 데이터베이스의 item 모델 인스턴스의 겉껍떼기 필드 등등의 양식만 참고하겠다." 라는 의미이다.
# 이제 전체적인 과정을 쉽게 순서대로 설명하자면,
# <elif GET 부분> (아마 내 개인적인 생각 및 추측으로는, 가장 먼저 발생하는 일은 list.html 파일에서 데이터 목록중 하나를 골라 수정하기 버튼을 누르면 그 데이터의 id값이 쿼리 파라미터로 보내져서 GET방식이 되고, 그 id값에 맞는 겉폼형식이 나타나는 과정이 아닐까 싶다.)
#   사용자가 쿼리 파라미터 id값을 지닌 url 사이트로 접속을 하면, 그 id값이 사이트 쿼리파라미터로 GET으로 보내지고,
#   그렇게 쿼리파라미터로 받은 데이터의 id값과 동일한 pk id값의 데이터베이스의 데이터 인스턴스를 item 변수에 넣어주고,
#   form = RestaurantForm(instance=item) 안에 request.POST 매개변수가 없으므로 값 교체 없이, 그저 item과 같은 형식(필드 등등 껍데기 형식만)으로 겉폼양식을 갖고와서 form 변수에 저장해준다.
#   그렇게 각 id값에 맞는 item 인스턴스 데이터의 모델폼의 겉폼양식을 갖고와서, 겉폼양식에 id에 매칭되는 필드 정보를 담은 수정 사이트 겉폼양식을 불러와서 update.html 파일로 렌더링 해준다.
# <라우팅을 통해 method=GET에서 POST로 전환>
#   이렇게, id에 맞는 수정 겉폼 양식이 불려와진 update.html 에서 수정을 완료하고 제출하면, 그게 POST방식으로 리퀘스트 값을 가지고 urls.py 파일을 거쳐서 views.py 파일의 update 메소드로 와서 if POST 부분을 실행하게 되는 과정이 된다.
# <if POST 부분>
#   예를들어 불러와진 수정 겉폼양식에서 id=2 쿼리 파라미터의 모델 인스턴스의 데이터 필드의 name과 address 부분의 내용을 수정하여, name='바뀐거'과 address='바뀐거'으로 수정하여 제출을 눌렀다면,
#   모델 인스턴스 데이터인 {id=2, name='원래꺼', address='원래꺼}가 아닌, {id=2, name='바뀐거', address='바뀐거'}가 request.POST 로 새로 입력한 모델 인스턴스가 리퀘스트값으로 보내진다.
#   그러면 리퀘스트된 모델 인스턴스의 pk=request.POST.get('id') 는 pk=2가 되고, 즉, item = Restaurant.objects.get(pk=request.POST.get('id')) 코드는 item = Restaurant.objects.get(pk=2) 가 되고, 이 코드의 의미는
#   이미 저장되어있는 데이터베이스에서 id=2인 모델 인스턴스를 불러와서 item 변수에 할당한다라는 의미인 것이다.
#   그러면 이제 form = RestaurantForm(request.POST, instance=item) 코드의 의미는, instance=item는 데이터베이스에서 불러온 item 모델 인스턴스의 형식(필드 목록 등등)을 참고하여, request.POST인 {id=2, name='바뀐거', address='바뀐거'}로 item과 같은 형식(필드 목록 등등의 형식만)의 모델 인스턴스를 만들어서 form 변수에 저장한다는 의미인 것이다.
#   즉, 수정 대상은 instance=item 이었고, 새로운 데이터는 request.POST 인 것이다.
#   하여튼 그렇게해서 form에 저장된 값을 유효성 검사를 하고 통과하면 form.save()로 임시가 아닌 완전히 데이터베이스에 값을 저장함으로써 업데이트가 된것이다.

def detail(request, id):  # urls.py 파일에서 패스파라미터로 id값을 받을수있게 해놨기때문에, 매개변수로 id를 추가로 넣을 수 있게되었다.
                         # 여기서 가장 중요한점은, 리퀘스트로 받아온것이 아니고 아예 패스파라미터로 메소드 매개변수로 id값을 가져온것이기 때문에 request.GET 이런거 필요없다.
    if id is not None:
        item = get_object_or_404(Restaurant, pk=id)  # 패스파라미터를 매개변수로 받아옴으로써, 더욱 간단하게 쓸 수 있게 됨.
    # if 'id' in request.GET:  # 만약 정상적으로 id가 왔을때
    #   item = get_object_or_404(Restaurant, pk=request.GET.get('id'))  # 정상적으로 id가 왔을때 그 id값에 매칭되는 모델 인스턴스가 데이터베이스에 존재하면 그걸 item에 할당해주고,
                                                                        # id는 잘 받았지만, id에 매칭되는 모델 인스턴스가 데이터베이스에 존재하지 않으면 404를 대신 item에 넣어준다.
                                                                        # 그러면, id값이 없는 데이터라 로딩이 안될때 사이트에 에러 안뜨고 'Page not found (404)'이라는 화면만 뜨고, 에러 내용이 뜨지 않는다.
                                                                        # 참고로 이건 shortcuts 소속 라이브러리 이다.
                                                                        # 결론적으로, item에 '가져온 id에 맞는 데이터베이스 데이터' 또는 '404'를 할당해준다는 것이다.
        reviews = Review.objects.filter(restaurant=item).all()  # 참고로 forms.py 파일의 모델폼을 쓰는것이 아니라, models.py 파일의 모델을 사용해야한다. 즉, 데이터베이스에 저장된건 models.py 파일의 변수니까 Review 를 사용해야하는 것이다.
        return render(request, 'third/detail.html', {'item': item, 'reviews': reviews})
    return HttpResponseRedirect('/third/list/')  # 만약 정상적으로 id가 오지않았을때(= 값이 제대로 전달되지 않았다), 리스트 화면으로 이동한다.

def delete(request, id):
    item = get_object_or_404(Restaurant, pk=id)
    if request.method == 'POST' and 'password' in request.POST:
        if item.password == request.POST.get('password') or item.password is None:  # 해당 id의 식당의 패스워드가 아직 정해지지않아 null값일때 그냥 바로 삭제할수있게 해줌.
            item.delete()
            return redirect('list')  # 리스트 화면으로 이동한다.
        return redirect('restaurant-detail', id=id) # 만약 비밀번호가 입력되지 않았다면 상세페이지로 되돌아감.
                                                    # 만약이게 html파일이었다면 <a href="{% url 'restaurant-detail' id=item.id %}"> </a> 와 같은 의미임.
                                                    # 즉, 패스파라미터로 id값을 넘겨주며 urls.py 파일의 path name이 restaurant-detail 인 곳으로 이동함.
    return render(request, 'third/delete.html', {'item': item})  # method가 GET으로 접근하였을때
                                                                 # 어떤 item의 삭제 메소드인지는 알아야하니까 {'item': item}도 렌더링해준다.
                                                                 # 참고로 third/delete.html 파일은, 삭제시 비밀번호 입력폼이다.


def review_create(request, restaurant_id):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():  # 데이터가 form 클래스에서 정의한 조건 (max_length 등)을 만족하는지 체크합니다.
            new_item = form.save()  # save 메소드로 입력받은 데이터를 레코드로 추가합니다.
        return redirect('restaurant-detail', id=restaurant_id)  # 리뷰작성이 끝났다면, 해당 레스토랑의 자세히보기 페이지로 다시이동시킴.
    item = get_object_or_404(Restaurant, pk=restaurant_id)  # 이 item은 바로 밑줄의 코드에서도 사용됨.
    form = ReviewForm(initial={'restaurant': item})  # 릴레이션 때문에 어느 레스토랑의 리뷰인지 미리 그 정보를 갖고와서 그거에 기반한 겉폼양식을 생성해놔야지 겉폼양식을 전달할수있기때문에 initial을 사용하였음. (예를들어, 이 리뷰는 5번 레스토랑의 리뷰니까 5번 겉폼양식을 갖다주라는 의미인 것이다.)
    return render(request, 'third/review_create.html', {'form': form, 'item':item})  # 겉폼양식과 현재 불러온 item 정보도 함께 두가지를 html파일로 넘겨준다.
                                                                                     # 굳이 item 까지 넘겨주는 이유는, review_create.html 파일에서 <form action="{% url 'review-create' restaurant_id=item.id %}" 부분의 item.id 부분으로 렌더링받은 item의 id 값을 갖고와야하기 때문이다.

def review_delete(request, restaurant_id, review_id):
    item = get_object_or_404(Review, pk=review_id)
    item.delete()
    return redirect('restaurant-detail', id=restaurant_id)  # 특정 레스토랑의 리뷰삭제후, 해당 레스토랑의 자세히보기 페이지인 이전화면으로 이동시킴.

def review_list(request):
    reviews = Review.objects.all().select_related().order_by('-created_at')  # 최신순으로 정렬
                                                                             # select_related()로 조인 해줌.
                                                                             # 설명하자면, select_related() 이거를 적어줌으로써, 
                                                                             # Review 모델클래스와 릴레이션되어있는 Restaurant 모델클래스의 정보까지 모두 들고와줌으로써 조인 해준것이다.
    paginator = Paginator(reviews, 10)  # 한 페이지에 10개씩 표시

    page = request.GET.get('page')  # 어떤 페이지의 조회를 원했는지 쿼리파라미터에서 page 데이터를 가져옴
    items = paginator.get_page(page)  # 해당 페이지에 들어있는 필드 정보들을 items에 넣음.

    context = {
        'reviews': items
    }
    return render(request, 'third/review_list.html', context)
