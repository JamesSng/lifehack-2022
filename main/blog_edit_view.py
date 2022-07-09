from flask import render_template, redirect, request, flash
import awstools

def blog_edit(blog):
    userinfo = awstools.getCurrentUserInfo()
    post = awstools.getBlogInfo(blog)
        
    if request.method == 'POST':
        result = request.form

        post['title'] = result['title']
        post['content'] = result['description']
        tags = ""
        for i in awstools.getBlogTags():
            print(i)
            print(result)
            print(i in result)
            if i in result:
                if tags != "":
                    tags += ", "
                tags += i
        post['tags'] = tags
        post['url'] = result['url']
        if 'publish' in result:
            post['published'] = not post['published']

        awstools.updateBlogInfo(blog, post)
        return redirect(f'/blog/{blog}')

    return render_template('blog_edit.html', userinfo=userinfo, post=post)

