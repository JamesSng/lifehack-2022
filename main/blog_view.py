from flask import render_template, redirect, request, flash
import awstools

def blog(blog):
    userinfo = awstools.getCurrentUserInfo()
    post = awstools.getBlogInfo(blog)
        
    tokens = post['content'].split(' ')
    arr = tokens[:min(100,len(tokens))]
    newString = ""
    for word in arr:
        newString = newString + word + " "
    if 100 < len(tokens):
        newString = newString + "[...]"
    post['shortContent'] = newString

    return render_template('blog.html', userinfo=userinfo, post=post)

