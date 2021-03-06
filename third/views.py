from django.shortcuts import render, get_object_or_404, redirect
from third.models import Restaurant, Review
from django.core.paginator import Paginator
from third.forms import RestaurantForm, ReviewForm, UpdateRestaurntForm
from django.http import HttpResponseRedirect
from django.db.models import Count, Avg

# Create your views here.
def list(request):
    # annotate 활용 study ! Count 안에 있는 review는 models의 class 내에 있는 변수다 (보이지 않아도 있음)
    restaurants = Restaurant.objects.all().annotate(reviews_count=Count('review')).annotate(average_point=Avg('review__point'))
    paginator = Paginator(restaurants, 5)
    
    page = request.GET.get('page')
    items = paginator.get_page(page)
    
    context = {
        'restaurants': items,
    }
    return render(request, 'third/list.html', context)

def create(request):
    if request.method == 'POST':
        form = RestaurantForm(request.POST)
        if form.is_valid():
            new_item = form.save()
        return HttpResponseRedirect('/third/list/')
    form = RestaurantForm()
    return render(request, 'third/create.html', {'form':form})

def update(request):
    if request.method == 'POST' and 'id' in request.POST:
        # item = Restaurant.objects.get(pk=request.POST.get('id'))
        item = get_object_or_404(Restaurant, pk=int(request.POST.get('id')))
        password = request.POST.get('password', '')
        form = UpdateRestaurntForm(request.POST, instance=item) # instance=item이어야 create가 아니라 update가 된다.
        if form.is_valid() and password == item.password:
            item = form.save()
            
    elif request.method == 'GET':
        # item = Restaurant.objects.get(pk=request.GET.get('id')) 
        item = get_object_or_404(Restaurant, pk=int(request.GET.get('id')))
        form = RestaurantForm(instance=item)
        return render(request, 'third/update.html', {'form':form})
    return HttpResponseRedirect('/third/list/')


def detail(request, id):
    if 'id' is not None:
        item = get_object_or_404(Restaurant, pk=id)
        reviews = Review.objects.filter(restaurant=item).all()
        return render(request, 'third/detail.html', {'item': item, 'reviews':reviews})
    return HttpResponseRedirect('third/list/')


def delete(request, id):
    item = get_object_or_404(Restaurant, pk=id)
    if request.method == 'POST' and 'password' in request.POST:
        if item.password == request.POST.get('password') or item.password is None:
            item.delete()
            return redirect('list')
        return redirect('restaurant-detail', id=id)
    return render(request, 'third/delete.html', {'item': item})


def review_create(request, restaurant_id):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            new_item = form.save()
        return redirect('restaurant-detail', id=restaurant_id)
    
    item = get_object_or_404(Restaurant, pk=restaurant_id)
    form = ReviewForm(initial={'restaurant': item})

    return render(request, 'third/review_create.html', {'form':form, 'item':item})


def review_delete(request, restaurant_id, review_id):
    item = get_object_or_404(Review, pk=review_id)
    item.delete()

    return redirect('restaurant-detail', id=restaurant_id)


def review_list(request):
    # select_related()를 써서 페이지에서 데이터를 호출하는 횟수를 (리뷰갯수)회에서 (1)회로 줄일 수 있다. 성능 향상.
    reviews = Review.objects.all().select_related().order_by('-created_at')
    paginator = Paginator(reviews, 10)

    page = request.GET.get('page')
    items = paginator.get_page(page)

    context = {
        'reviews':items
    }

    return render(request, 'third/review_list.html', context)

