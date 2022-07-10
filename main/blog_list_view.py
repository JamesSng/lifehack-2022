from flask import render_template, redirect, request, flash
import awstools

def blog_list():
    username = request.args.get('user')
    usertype = request.args.get('usertype')
    if usertype:
        usertype = int(usertype)
    tags = ""
    friends = False

    userinfo = awstools.getCurrentUserInfo()
    posts = awstools.getAllBlogPosts()
    for post in posts:
        newString = post['content'][:min(500, len(post['content']))]
        while newString and not newString[-1].isspace():
            newString = newString[:-1]
        if len(newString) != len(post['content']):
            newString += "[...]"
        newString = newString.replace('\n', '<br>')
        post['shortContent'] = newString

    if request.method == 'POST' or username or usertype:
        result = request.form

        if 'create' in result:
            blogid = awstools.getNextBlogId()
            username = userinfo['username'] if userinfo['usertype'] == 0 else userinfo['organiserid']
            usertype = userinfo['usertype']
            name = userinfo['name']
            awstools.createBlogFromId(blogid, username, usertype, name)
            return redirect(f'/edit_blog/{blogid}')

        if not username:
            username = result['username']
        if usertype == None:
            if result['usertype'] == 'Volunteer':
                usertype = [0]
            elif result['usertype'] == 'Organiser':
                usertype = [1]
            else:
                usertype = [0, 1]
        else:
            usertype = [usertype]
        
        tags = ""
        for i in awstools.getBlogTags():
            if i in result:
                tags += i + " "
        friends = 'friends' in result
        
        if username:
            posts = [i for i in posts if username == i['authorid']]
        if usertype:
            posts = [i for i in posts if int(i['authortype']) in usertype]
        if tags:
            newposts = []
            for i in posts:
                valid = True
                for j in posts['tags'].split(','):
                    if j.strip() not in tags:
                        valid = False
                if valid:
                    newposts.append(i)
            posts = newposts
        if friends and userinfo != None and userinfo['usertype'] == 0:
            posts = [i for i in posts if i['authortype'] == 0 and i['authorid'] in userinfo['friends']]
    
    if username == None or username == "None":
        username = ""
    return render_template('blog_list.html', userinfo=userinfo, posts=posts, username=username, tags=tags, friends=friends)

