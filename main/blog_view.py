from flask import render_template, redirect, request, flash
import awstools

def blog(blog):
    userinfo = awstools.getCurrentUserInfo()
    post = awstools.getBlogInfo(blog)

    blog = int(blog)
    published = awstools.getPublishedBlogs()
    if blog not in published:
        flash('This blog does not exist!', 'warning')
        return redirect('/blogs')
    index = published.index(blog)
        
    return render_template('blog.html', userinfo=userinfo, post=post, index=index, published=published)

