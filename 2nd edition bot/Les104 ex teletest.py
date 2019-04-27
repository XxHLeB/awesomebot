import codecs


city = 'New york'
#try:
  #  f = open("list_of_cities.txt", 'a')
   # print(f.write(str(city + '\n')))
   # f.close()
   # f = open("list_of_cities.txt", 'r')
   # print(f.read())
   # f.close()
#   # print('Ошибка записи файла', e)
    
with codecs.open('list_of_cities.txt','a', "utf-8") as f: 
    print(f.write(str('\n' + city)))
    f.close()
    
with codecs.open('list_of_cities.txt','r', "utf-8") as f: 
    print(f.read())
    f.close()    
   