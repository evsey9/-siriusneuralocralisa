
# coding: utf-8

# # Начало

# ### Предобработка

# In[3]:

from skimage import io
import numpy as np
import os
from PIL import Image
import requests
from io import BytesIO

# In[4]:

def main(url = "", *kwargs):
    if url == "":
        return("Введите URL.")
    try:
        response = requests.get(url)
        image = Image.open(BytesIO(response.content))
        image = image.convert("L")
    except:
        return("Введите правильный URL.")

    # In[5]:


    sz = image.size
    img_np = np.array (image.getdata())
    img_np = img_np.reshape(sz[::-1])


    # In[4]:


    mean = img_np.mean()
    mean -= 10
    #print(mean)
    img_np1 = np.zeros(img_np.shape)
    for i in range(img_np.shape[0]):
        for j in range(img_np.shape[1]):
            if img_np[i,j] < mean:
                img_np1[i][j] = 0
            else:
                img_np1[i][j] = 255
    img_np = img_np1


    # ### Разделение на строки

    # In[6]:


    h1 = np.sum(img_np, axis = 1)
    maximum = h1.max()


    # In[7]:


    def str_split (in_arr, out_list, acc=None, m=None):
        if acc == None:
            acc = 8
        if m == None:
            m = in_arr.shape[1]*255
        b = False
        if out_list == None:
            out_list = []
            b = True
        prev = 0
        r = 0
        for i in range(in_arr.shape[0]):
            if np.sum(in_arr[i])//255 >= maximum//255 - acc and np.sum(in_arr[i])//255 <= maximum//255 + acc or i == in_arr.shape[0]-1:
                if i-prev >= 5:
                    out_list.append(in_arr[prev:i])
                    r += 1
                prev = i
        if b == True:
            in_arr = out_list
        return r


    # In[8]:


    str_list = []
    strlen = []
    str_split(img_np, str_list, acc=8, m=h1.max())
    str_list = np.array(str_list)
    strlen = np.array([i.shape[0] for i in str_list])


    # Итак, у нас есть сейчас:
    #
    # <code>img_np</code>:
    # Массив с закодированной картинкой;
    #
    # <code>h1</code>:
    # сумма кодов в строчке пикселей;
    #
    # <code>str_list</code>:
    # список двумерных массивов строк текста;
    #
    # <code>strlen</code>:
    # список ширин строк текста

    # In[9]:


    strlens = sorted(strlen)
    mid = len(strlens)//2
    norm = strlens[mid]
    str_list_new = []
    i = 0
    while i < len(str_list):
        arr_now = str_list[i]
        if str_list[i].shape[0] > norm*1.3:
            i1 = norm
            accuracy = 13
            str_split(arr_now, str_list_new, acc=accuracy, m=h1.max())
        else:
            str_list_new.append(arr_now)
        i += 1
    str_list = np.array(str_list_new)
    # In[10]:
    sep_arr = str_list[0]
    for i in range(1, len(str_list)):
        sep_arr = np.vstack((sep_arr, np.zeros(str_list[0].shape[1]), np.zeros(str_list[0].shape[1]), str_list[i]))


    # In[11]:




    # представим, что это работает

    # ## Разделение на слова

    # In[ ]:


    def word_split(in_arr, out_list=None, acc=None, m=None):
        if acc == None:
            acc = 8
        if m == None:
            m = in_arr.shape[0]*255
        b = False
        if out_list == None:
            out_list = []
            b = True
        prev = 0
        r = 0
        letter_ignore = 0
        for i in range(in_arr.shape[1]):
            if np.sum(in_arr[:,i])//255 >= m//255 - acc and np.sum(in_arr[:,i])//255 <= m//255 + acc or i == in_arr.shape[1]-1:
                if letter_ignore >= 3:
                    if i-prev >= 5:
                        out_list.extend(in_arr[:,prev:i])
                        r += 1
                    prev = i
                    letter_ignore = 0
                else:
                    letter_ignore += 1
        if b == True:
            in_arr = out_list
        return r


    # In[ ]:


    word_list = []
    for i in range(str_list.shape[0]):
        str_arr = str_list[i]
        word_split(str_arr, acc=2)
        word_list.append(str_arr)
    word_list = np.array(word_list)
    return("Программа работает")

    # In[14]:




