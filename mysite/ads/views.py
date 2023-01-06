from ads.models import Ad, Comment, Fav
from ads.owner import OwnerListView, OwnerDetailView, OwnerCreateView, OwnerUpdateView, OwnerDeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from ads.pics.forms import CreateForm, CommentForm
from django.http import HttpResponse
from django.db.models import Q
from django.contrib.humanize.templatetags.humanize import naturaltime

class AdListView(OwnerListView):
    model = Ad
    template_name = "ads/ad_list.html"

    def get(self, request):
            ad= Ad.objects.all()
            favorites = list()
            if request.user.is_authenticated:
                # rows = [{'id': 2}, {'id': 4} ... ]  (A list of rows)
                rows = request.user.favorite_ads.values('id')
                # favorites = [2, 4, ...] using list comprehension
                favorites = [ row['id'] for row in rows ]
                        # Augment the post_list
            for obj in ad:
                obj.natural_updated = naturaltime(obj.updated_at)

            to_search = request.GET.get('search', False)
            if to_search:
                query = Q(title= to_search) 
                query.add(Q(text=to_search), Q.OR)
                ad = Ad.objects.filter(query).select_related().order_by('-updated_at')[:10]
                print(ad)
                ctx = {'object' : ad, 'favorites': favorites}
                return render(request, self.template_name, ctx)
            else:
                ctx = {'object' : ad, 'favorites': favorites}
                return render(request, self.template_name, ctx)
            
        
    # By convention:
    #template_name = "myarts/article_list.html"

class AdDetailView(OwnerDetailView):
    model = Ad
    template_name= 'ads/ad_detail.html'
    def get(self, request, pk) :
        x = Ad.objects.get(id=pk)
        comments = Comment.objects.filter(ad=x).order_by('-updated_at')
        comment_form = CommentForm()
        context = { 'object' : x, 'comments': comments, 'comment_form': comment_form }
        return render(request, self.template_name, context)

class AdCreateView(LoginRequiredMixin, View):
    success_url = reverse_lazy('ads:all')
    template_name = 'ads/ad_form.html'

    def get(self, request, pk=None):
        form = CreateForm()
        ctx = {'form': form}
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None):
        form = CreateForm(request.POST, request.FILES or None)

        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template_name, ctx)

        # Add owner to the model before saving
        pic = form.save(commit=False)
        pic.owner = self.request.user
        pic.save()
        form.save_m2m()    # Add this
        return redirect(self.success_url)


class AdUpdateView(LoginRequiredMixin, View):
    success_url = reverse_lazy('ads:all')
    template_name = 'ads/ad_form.html'

    def get(self, request, pk):
        ad = get_object_or_404(Ad, id=pk, owner=self.request.user)
        form = CreateForm(instance=ad)
        ctx = {'form': form}
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None):
        ad = get_object_or_404(Ad, id=pk, owner=self.request.user)
        form = CreateForm(request.POST, request.FILES or None, instance=ad)

        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template_name, ctx)

        ad = form.save(commit=False)
        ad.save()
        form.save_m2m()  
        return redirect(self.success_url)


class AdDeleteView(OwnerDeleteView):
    model = Ad


def stream_file(request, pk):
    pic = get_object_or_404(Ad, id=pk)
    response = HttpResponse()
    response['Content-Type'] = pic.content_type
    response['Content-Length'] = len(pic.picture)
    response.write(pic.picture)
    return response

# Views for Ads comment
class CommentCreateView(LoginRequiredMixin, View):
    success_url = reverse_lazy('ads:all')
    def post(self, request, pk) :
        f = get_object_or_404(Ad, id=pk)
        comment = Comment(text=request.POST['comment'], owner=request.user, ad=f)
        comment.save()
        return redirect(reverse('ads:ad_detail', args=[pk]))

class CommentDeleteView(OwnerDeleteView):
    model = Comment
    template_name = "ads/comment_delete_confirmation.html"

    def get_success_url(self):
        ad = self.object.ad
        return reverse('ads:ad_detail', args=[ad.id])


# csrf exemption in class based views
# https://stackoverflow.com/questions/16458166/how-to-disable-djangos-csrf-validation
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.utils import IntegrityError

@method_decorator(csrf_exempt, name='dispatch')
class AddFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        print("Add PK",pk)
        t = get_object_or_404(Ad, id=pk)
        fav = Fav(user=request.user, ad=t)
        try:
            fav.save()  # In case of duplicate key
        except IntegrityError as e:
            pass
        return HttpResponse()

@method_decorator(csrf_exempt, name='dispatch')
class DeleteFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        print("Delete PK",pk)
        t = get_object_or_404(Ad, id=pk)
        try:
            fav = Fav.objects.get(user=request.user, ad=t).delete()
        except Fav.DoesNotExist as e:
            pass

        return HttpResponse()





# class AdCreateView(OwnerCreateView):
#     model = Ad
#     # List the fields to copy from the Article model to the Article form
#     fields = ['title', 'text', 'price', 'picture']

# class AdUpdateView(OwnerUpdateView):
#     model = Ad
#     fields = ['title', 'text']
#     # This would make more sense
#     # fields_exclude = ['owner', 'created_at', 'updated_at']
