from flask import render_template, redirect, request, flash
import awstools

def blog_list():
    userinfo = awstools.getCurrentUserInfo()
    posts = awstools.getAllBlogPosts()
    for post in posts:
        newString = post['content'][:min(500, len(post['content']))]
        while not newString[-1].isspace():
            newString = newString[:-1]
        if len(newString) != len(post['content']):
            newString += "[...]"
        newString = newString.replace('\n', '<br>')
        post['shortContent'] = newString

    return render_template('blog_list.html', userinfo=userinfo, posts=posts)

