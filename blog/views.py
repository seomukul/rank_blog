from django.db.models import Count, Q
from django.core.mail import send_mail
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.http import require_POST
from django.views.generic import ListView
from django.contrib import messages
from .forms import CommentForm, EmailPostForm
from .models import Category, Post
from taggit.models import Tag




def about (request):
    return render(request, 'blog/about.html')

def thanks(request):
    return render(request, 'blog/thanks.html')

def post_list(request, tag_slug=None):
    tag = None
    post_list = Post.published.all()
    popular_posts = Post.published.order_by('-publish')[:3]  # Get the top 3 popular posts

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = post_list.filter(tags__in=[tag])

    paginator = Paginator(post_list, 3)  # 3 posts per page
    page_number = request.GET.get('page')
    
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver the last page
        posts = paginator.page(paginator.num_pages)

    # Example categories, you might want to fetch these from your database
    categories = ['Technology', 'Design', 'Business']  # Replace with actual category fetching logic

    return render(
        request,
        'blog/post/list.html',
        {
            'posts': posts,
            'tag': tag,
            'popular_posts': popular_posts,
            'categories': categories,
        }
    )


class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'


def post_detail(request, category_slug, slug):
    post = get_object_or_404(Post, category__slug=category_slug, slug=slug, status=Post.Status.PUBLISHED)
    comments = post.comments.filter(active=True)
    form = CommentForm()

    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]

    return render(
        request,
        'blog/post/detail.html',
        {
            'post': post,
            'comments': comments,
            'form': form,
            'similar_posts': similar_posts
        }
    )

def category_posts(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    posts = Post.published.filter(category=category)
    
    # Add pagination
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    # Get categories for sidebar
    categories = Category.objects.all()
    
    return render(
        request,
        'blog/post/list.html',
        {
            'category': category,
            'posts': posts,
            'categories': categories,
            'section': 'category',
        }
    )

def search(request):
    query = request.GET.get('q', '')
    if query:
        # Search in title and body
        posts = Post.published.filter(
            Q(title__icontains=query) |
            Q(body__icontains=query)
        ).order_by('-publish')
    else:
        posts = Post.published.none()
    
    # Pagination
    paginator = Paginator(posts, 10)  # 10 posts per page
    page = request.GET.get('page')
    
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render(request, 'blog/post/search.html', {
        'query': query,
        'posts': posts,
    })

def contact (request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        message = request.POST.get('message')
        invalid_imput = ['', ' ']
        if name in invalid_imput or email in invalid_imput or phone in invalid_imput or message in invalid_imput:
            messages.error(request, 'One or more fields are empty!')
        else:
            email_pattern = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
            phone_pattern = re.compile(r'^[0-9]{10}$')

            if email_pattern.match(email) and phone_pattern.match(phone):
                form_data = {
                'name':name,
                'email':email,
                'phone':phone,
                'message':message,
                }
                message = '''
                From:\n\t\t{}\n
                Message:\n\t\t{}\n
                Email:\n\t\t{}\n
                Phone:\n\t\t{}\n
                '''.format(form_data['name'], form_data['message'], form_data['email'],form_data['phone'])
                send_mail('You got a mail!', message, '', ['dev.ash.py@gmail.com'])
                messages.success(request, 'Your message was sent.')
                # return HttpResponseRedirect('/thanks')
            else:
                messages.error(request, 'Email or Phone is Invalid!')
    return render(request, 'blog/contact.html', {})


def post_share(request, slug):
    # Retrieve post by slug
    post = get_object_or_404(Post, slug=slug, status=Post.Status.PUBLISHED)
    sent = False

    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends you read '{post.title}'"
            message = f"Read '{post.title}' at {post_url}\n\n{cd['name']}'s comments: {cd['comments']}"
            send_mail(subject, message, cd['email'], [cd['to']])
            sent = True
    else:
        form = EmailPostForm()

    return render(request, 'blog/post/share.html', {'post': post, 'form': form, 'sent': sent})


@require_POST
def post_comment(request, slug):
    post = get_object_or_404(Post, slug=slug, status=Post.Status.PUBLISHED)
    comment = None
    form = CommentForm(data=request.POST)
    
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()
        messages.success(request, 'Your comment has been added.')
        return redirect(post.get_absolute_url())
    
    return render(
        request,
        'blog/post/comment.html',
        {
            'post': post,
            'form': form,
            'comment': comment
        }
    )

def subscribe(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            # Here you can add code to save the email to your database
            # or integrate with your email service provider
            messages.success(request, 'Thank you for subscribing!')
        else:
            messages.error(request, 'Please provide a valid email address.')
    return redirect(request.META.get('HTTP_REFERER', 'blog:post_list'))
