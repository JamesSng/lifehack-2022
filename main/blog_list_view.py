from flask import render_template, redirect, request, flash
import awstools

def blog_list():
    userinfo = awstools.getCurrentUserInfo()
    posts = awstools.getAllBlogPosts()
    for post in posts:
        tokens = post['content'].split(' ')
        arr = tokens[:min(100,len(tokens))]
        newString = ""
        for word in arr:
            newString = newString + word + " "
        if 100 < len(tokens):
            newString = newString + "[...]"
        post['shortContent'] = newString

    return render_template('blog_list.html', userinfo=userinfo, posts=posts)

