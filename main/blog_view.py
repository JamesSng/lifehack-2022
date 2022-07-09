from flask import render_template, redirect, request, flash
import awstools

def blog(blog):
    userinfo = awstools.getCurrentUserInfo()
    post = awstools.getBlogInfo(blog)

    blog = int(blog)
    published = awstools.getPublishedBlogs()
    if blog not in published:
        if userinfo != None and userinfo['usertype'] == post['authortype'] and userinfo['name'] == post['authorname']:
            return redirect(f'/edit_blog/{blog}')
        flash('This blog does not exist!', 'warning')
        return redirect('/blogs')
    index = published.index(blog)

    post['content'] = post['content'].replace('\n', '<br>')
    post['reversed_comments'] = reversed(post['comments'])

    if request.method == 'POST':
        result = request.form

        text = result['comment-text']
        name = userinfo['name']
        
        userid = userinfo['username'] if userinfo['usertype'] == 0 else userinfo['organiserid']
        post['comments'].append({'authorname': name, 'text':text, 'userid':userid, 'usertype':userinfo['usertype']})
        awstools.updateBlogInfo(blog, post)

        return redirect(f'/blog/{blog}')
        
    return render_template('blog.html', userinfo=userinfo, post=post, index=index, published=published)

