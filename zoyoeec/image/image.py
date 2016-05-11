### Reource view

##
# fetch the first image of a item by its refid
# FIXME: dont create small images all the time
##
@zuser.authority_item
def fetchimagebyrid(request,itemid):
  picture = None
  item = Item.getItemByRID(itemid)
  if item:
    image = item.getImage(0)
    if image:
      if ("sc" in request.GET):
         if image.small:
            picture = image.small
         elif image.image:
            image.small = createsc(image.image)
            try:
              image.put()
            except RequestTooLargeError:
              pic = rescale(image.image,600,600)
              image.image = pic
              image.put()
              del pic
            picture = image.small
         else:
            picture = None
      else:
         picture = image.image
    else:
      picture = None
  else:
    picture = None
  if picture:
    return HttpResponse(picture, mimetype="image/jpeg")
  else:
    return  HttpResponseRedirect('/static/res/picnotfound.jpg')


def fetchimage(request,supplier,key,index="0"):
  item = Item.get_by_id(int(key),parent = Supplier.getSupplierByName(supplier))
  picture = None
  idx = int(index)
  if item:
    image = item.getImage(idx)
    if image:
      if ("sc" in request.GET):
         if image.small:
            picture = image.small
         elif image.image:
            image.small = createsc(image.image)
            try:
              image.put()
            except RequestTooLargeError:
              pic = rescale(image.image,600,600)
              image.image = pic
              image.put()
              del pic
            picture = image.small
         else:
            picture = None
      else:
         picture = image.image
    else:
      picture = None
  else:
    picture = None
  if picture:
    return HttpResponse(picture, mimetype="image/jpeg")
  else:
    return  HttpResponseRedirect('/static/res/picnotfound.jpg')

# Used for uploading image files


##
# FIXME: This should be moved into rest api
#
##
def rotateimage(request,supplier,key,index="0"):
  item = Item.get_by_id(int(key),parent = Supplier.getSupplierByName(supplier))
  idx = int(index)
  if item:
    image = item.getImage(int(idx))
    if image:
      gimg = images.Image(image.image)
      gimg.rotate(90)
      image.image = gimg.execute_transforms()
      image.put()
  return HttpResponse("ok")

###
# 
# Uploading image for item
#
###
@zuser.authority_item
def uploadimage(request,supplier,key,index='0'):
  __register_admin_action(request,"uploadimage",supplier+"/"+key)
  #file = request.FILES['image'].read()
  #type = request.FILES['image'].content_type
  #image = request.FILES['image'].content_type_extra
  file = request.FILES['image'].read()
  picture = rescale(file,600,600)
  item = Item.get_by_id(int(key),parent = getSupplierByName(supplier))
  idx = int(index)
  if item:
    img = item.getImage(idx)
    if img:
      img.image = picture
    else:
      img = ImageData(image=picture,name=item.name,parent=item,idx=idx) 
      img.url = "http://" + request.META['HTTP_HOST'] + "/admin/fetchimage/" + supplier + "/" + key + "/" + str(idx)
    img.small = createsc(picture)
    img.put()
    del picture
    item.galleryurl = img.url
    item.put()
    return HttpResponse("ok")
  else:
    return HttpResponse("fail")

####
#  A view for userd to upload multiply images for a supplier
#
####
@zuser.authority_item
@ebay_view_prefix
def uploadimages(request):
  supplier = "Anonymous"
  if 'supplier' in request.GET:
    supplier = request.GET['supplier']
  context = {'SUPPLIER':supplier}
  return (render_to_response("admin/images.html",context,context_instance=RequestContext(request)))


# Fix urls for ImageData
#
#
def checkurl(request):
  imgs = ImageData.all()
  for img in imgs:
    img.url = "http://" + request.META['HTTP_HOST'] + "/admin/fetchimage/" + img.parent().parent().name + "/" + str(img.parent().key().id()) + "/" + str(img.idx) +"/"
    img.put()
  return HttpResponse("ok")

