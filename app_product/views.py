from django.shortcuts import render, redirect
#from django.http import request
import requests
import pandas
import time
from .models import Product, DocumentType, RemainderHistory, Report, Identifier, ProductCategory
import datetime
import pytz
from django.contrib import messages
import xlwt
from django.http import HttpResponse, JsonResponse


def dashboard(request):
    if request.user.is_authenticated:
        categories=ProductCategory.objects.all()
        context = {
            'categories': categories,
        }
        return render(request, 'dashboard.html', context)
    else:
        return redirect ('login_page')

def create_product(request):
    if request.method == "POST":
        file = request.FILES["file_name"]
        # print(file)
        # df1 = pandas.read_excel('Delivery_21_06_21.xlsx')
        df1 = pandas.read_excel(file)
        cycle = len(df1)
        for i in range(cycle):
            row = df1.iloc[i]#reads each row of the df1 one by one
            article=row.Article
            if '/' in str(article):
                article=article.replace('/', '_')
            category=row.Category
            #====================getting rid of extra spaces in the string==================================
            #category=category.replace(' ', '')#getting rid of extra spaces
            #category=category.strip()#getting rid of extra spaces at both sides of the string
            category=category.split()
            category=' '.join(category)
            #============================end of block=======================================================
            #====================getting rid of extra spaces in the string==================================
            #article=article.replace(' ', '')#getting rid of extra spaces
            #article=article.strip()#getting rid of extra spaces at both sides of the string
            article=article.split()
            article=' '.join(article)
            #============================end of block=======================================================
            category=ProductCategory.objects.get(name=category)
            if Product.objects.filter(article=article).exists():
                product=Product.objects.get(article=article)
                product.name=row.Title
                product.save()
            else:
                product = Product.objects.create(
                    name=row.Title,
                    article=article, #without extra spaces
                    auto_model=row.Model, 
                    category=category    
                )
            #==========Ozon import module==========================
            #Озон воспринимает товар как уже существующий, если у него совпадают обязательные аттрибуты.
            #Достаточно изменить один их них, чтобы Озон создал новый товар

            #если значение aттрибута 'dictionary_value_id' больше нуля, нужно открывать данный аттрибут через
            #https://api-seller.ozon.ru/v1/description-category/attribute/values и смотреть идентификационный номер
            #и текстовое значение нужные нам. И их указыать в соответствующем аттрибуте

            #Сначала мы создаём новый товар на площадке Ozon посредством метода: 
            #response=requests.post('https://api-seller.ozon.ru/v3/product/import', json=task, headers=headers)
            #В процессе содания нового товара Ozon присваивает ему уникальный Ozon_id, но не изменяет кол-во товара на стоке Ozon
            #Изменение в кол-во товара на стоке Оzon вносятся позднее при проведении Автоматического поступления

            #Далее получаем ozon_id посредством метода:
            #response=requests.post('https://api-seller.ozon.ru/v2/product/list', json=task_2, headers=headers)
            #и сохраняем в модели Product

            #Ozon_id и offer_id нужны для дальнейшего редактирования количества товара на стоке озон посредством метода:
            #response=requests.post('https://api-seller.ozon.ru/v2/products/stocks', json=task_3, headers=headers)
            #offer_id это номер товара уникальный в erms. 
            #В качестве offer_id для аксов мы используем imei. Можно использовать EAN товара. Это удобно в случае с аксами,
            #но при работе со смартфонами EAN не всегда известен. IMEI использовать не получится, так как один SKU может иметь разные IMEI.

            #я пытался создать товар и задать ему количество в одной функции, но Озону нужно время для того, чтобы проверить,
            #что я создал у него на площадке, и он возвращает нужныйм нам ozon_id только через какое-то время, а не сразу
            #поэтому я разделил эти две функции. Сначала мы создаем товар (def ozon_product_create), а затем уже задаем нужное
            #количество (def delivery_auto)

            #checking if product already has Ozon_id & does not have to be created again
            #if product.ozon_id is None:
            headers = {
                "Client-Id": "1711314",
                "Api-Key": 'b54f0a3f-2e1a-4366-807e-165387fb5ba7'
            }

            if 'Дефлектор капота' in row.Title:              
                # key_word=  f"""дефлектор, дефлектор капота, дефлектор капота для {product.auto_model}, дефлектор капота {product.auto_model}, 
                # мухобойка, мухобойка для {product.auto_model}, мухобойка {product.auto_model}, отбойник, отбойник для {product.auto_model},
                # отбойник {product.auto_model},
                # """
                key_word=  f"""{row.Russian_Brand}, {row.Russian_Model}, {row.Russian_Brand} {row.Russian_Model} дефлектор, дефлектор {row.AutoModel}, дефлектор для {row.AutoModel}, дефлектор {row.AutoBrand}, дефлектор для {row.AutoBrand}, дефлектор {row.AutoBrand} {row.AutoModel}, дефлектор {row.Russian_Brand}, дефлектор {row.Russian_Model}, дефлектор для {row.AutoBrand} {row.AutoModel}, 
дефлектор капота, дефлектор капота для {row.AutoBrand}, дефлектор капота {row.AutoBrand}, дефлектор капота для {row.AutoBrand} {row.AutoModel}, дефлектор капота {row.AutoBrand} {row.AutoModel}, дефлектор капота {row.AutoModel}, дефлектор капота для {row.AutoModel},
мухобойка, мухобойка для {row.AutoBrand}, мухобойка {row.AutoBrand}, мухобойка для {row.AutoBrand} {row.AutoModel}, мухобойка {row.AutoBrand} {row.AutoModel}, мухобойка {row.AutoModel}, мухобойка для {row.AutoModel},
отбойник, отбойник для {row.AutoBrand}, отбойник {row.AutoBrand}, отбойник для {row.AutoBrand} {row.AutoModel}, отбойник {row.AutoBrand} {row.AutoModel}, отбойник {row.AutoModel}, отбойник для {row.AutoModel},
{row.AutoModel}, {row.AutoBrand}, {row.AutoBrand} {row.AutoModel}"""
                
                description_string = f"""Дефлектор капота (мухобойка) разработан специально для {product.auto_model} ({row.Russian_Brand} {row.Russian_Model}), выполнен из гибкого оргстекла, представляет собой тонкую, просчитанную пластину.

Устанавливается на капот при помощи креплений, которые идут в комплекте, в штатные места в усилителе капота вашего автомобиля.

Расстояние между капотом и дефлектором примерно равно 1 см, оно продувается и промывается на мойке.

Дефлектор защищает фронтальную часть капота от повреждений и царапин. Он отражает камни и песок от впереди идущих машин, сохраняя лакокрасочное покрытие капота целым. Также дефлектор изменяет воздушный поток, уменьшает загрязнение лобового стекла и щёток стеклоочистителя.

В быту дефлектор капота еще называют отбойник или мухобойка, так как помимо камешков он отражает и летящих навстречу машине насекомых.

Цвет дефлектора капота тёмный, тонированный до 20%, на машине он будет выглядеть полностью чёрным. Дефлектор - это не только функциональный атрибут, но и стильный элемент тюнинга, который выгодно выделит на фоне других ваше авто."""
                

                task = {
                    "items": [
                        {
                            "attributes": [
                                #====================================
                                # is required: true
                                # Бренд
                                {
                                    "complex_id": 0,
                                    "id": 85,
                                    "values": [
                                        {
                                            "dictionary_value_id": 0,
                                            "value": "Нет бренда"
                                        }
                                    ]
                                },
                                #=====================================
                                # is required: true
                                # Партномер(article)
                                # Уникальный код (артикул*) однозначно идентифицирующий деталь автомобиля. 
                                # *Маркировка завода-изготовителя автомобиля для OE (оригинальных) запчастей или 
                                # номер детали по каталогу фирмы-производителя для OEM (не оригинальных). 
                                # Если такого артикула у вас нет- продублируйте сюда артикул товара
                                {
                                    "complex_id": 0,
                                    "id": 7236,
                                    "values": [
                                        {
                                            "dictionary_value_id": 0,
                                            "value": str(row.Article)
                                        }
                                    ]
                                },
                                #=======================================
                                # is required: true
                                # Тип
                                # Цифро-буквенный код товара для его учета,  
                                # является уникальным среди товаров бренда. Не является EAN/серийным  
                                # номером/штрихкодом, не равен названию модели товара - для этих параметров
                                # есть отдельные атрибуты. Артикул выводится в карточке товара на сайте и может
                                # спользоваться при автоматическом формировании названия товара.
                                {
                                    "complex_id": 0,
                                    "id": 8229,
                                    "values": [
                                        {
                                            "dictionary_value_id": 94656,
                                            "value": "Дефлектор капота"
                                        }
                                    ]
                                },
                                #===========================================
                                # is required: true
                                # Код продавца
                                # Цифро-буквенный код товара для его учета,  
                                # является уникальным среди товаров бренда. Не является EAN/серийным  
                                # номером/штрихкодом, не равен названию модели товара - для этих параметров
                                # есть отдельные атрибуты. Артикул выводится в карточке товара на сайте и может
                                # спользоваться при автоматическом формировании названия товара.
                                {
                                    "complex_id": 0,
                                    "id": 9024,
                                    "values": [
                                        {
                                            "dictionary_value_id": 0,
                                            "value": article
                                        }
                                    ]
                                },
                                #===========================================
                                #is required: True
                                #"Название модели (для объединения в одну карточку)",
                                #"Укажите название модели товара. Не указывайте в этом поле тип и бренд."
                                #Чтобы объединить две карточки, для каждой передайте 9048 в массиве attributes. 
                                #Все атрибуты в этих карточках, кроме размера или цвета, должны совпадать.
                                {
                                    "complex_id": 0,
                                    "id": 9048,
                                    "values": [
                                        {
                                            "dictionary_value_id": 0,
                                            "value": str(row.Model)
                                        }
                                    ]
                                },
                                #=============================================
                                #is required: false
                                #Название
                                #Название пишется по принципу:\nТип + Бренд + Модель (серия + пояснение) + Артикул производителя + , (запятая) + Атрибут\n
                                # Название не пишется большими буквами (не используем caps lock).\n
                                # Перед атрибутом ставится запятая. Если атрибутов несколько, они так же разделяются запятыми.\n
                                # Если какой-то составной части названия нет - пропускаем её.\n
                                # Атрибутом может быть: цвет, вес, объём, количество штук в упаковке и т.д.\n
                                # Цвет пишется с маленькой буквы, в мужском роде, единственном числе.\n
                                # Слово цвет в названии не пишем.\nТочка в конце не ставится.\n
                                # Никаких знаков препинания, кроме запятой, не используем.\n
                                # Кавычки используем только для названий на русском языке.\n
                                # Примеры корректных названий:\n
                                # Смартфон Apple iPhone XS MT572RU/A, space black \n
                                # Кеды Dr. Martens Киноклассика, бело-черные, размер 43\n
                                # Стиральный порошок Ariel Магия белого с мерной ложкой, 15 кг\n
                                # Соус Heinz Xtreme Tabasco суперострый, 10 мл\n
                                # Игрушка для животных Четыре лапы \"Бегающая мышка\" БММ, белый",
                                {
                                    "complex_id": 0,
                                    "id": 4180,
                                    "values": [
                                        {
                                            "dictionary_value_id": 0,
                                            "value": str(row.Title)
                                        }
                                    ]
                                },
                                #==================================================
                                # is required: False
                                # Аннотация
                                # Описание товара, маркетинговый текст. Необходимо заполнять на русском языке
                                {
                                    "complex_id": 0,
                                    "id": 4191,
                                    "values": [
                                        {
                                            "dictionary_value_id": 0,
                                            "value": description_string
                                        }
                                    ]
                                },
                                # is required: False
                                # Размеры, мм
                                # Размеры сторон товара без упаковки – длина х ширина х высота в миллиметрах 
                                # (указывать через Х). Длина – самая большая сторона, высота – самая маленькая
                                # {
                                #     "complex_id": 0,
                                #     "id": 4382,
                                #     "values": [
                                #         {
                                #             "dictionary_value_id": 0,
                                #             "value": "1500X500X100"
                                #         }
                                #     ]
                                # },
                                #==========================================================
                                # is required: False
                                # Комплектация
                                # Перечислите, что входит в комплект вместе с товаром
                                {
                                    "complex_id": 0,
                                    "id": 4384,
                                    "values": [
                                        {
                                            "dictionary_value_id": 0,
                                            "value": "Дефлектор капота (мухобойка), крепеж, инструкция"
                                        }
                                    ]
                                },
                                #============================================
                                #is requried: False
                                #guarantee period
                                {
                                   "complex_id": 0,
                                   "id": 4385,
                                   "values": [
                                       {
                                          "dictionary_value_id": 0,
                                           "value": "12 месяцев"
                                       }
                                  ]
                                },
                                #==================================================
                                #is requred: False
                                #Country of manufacture
                                {
                                    "complex_id": 0,
                                    "id": 4389,
                                    "values": [
                                        {
                                            "dictionary_value_id": 90295,
                                            "value": "Россия"
                                        }
                                    ]
                                },
                                #=====================================
                                #is required: False
                                #Вес с упаковкой, г
                                # {
                                #     "complex_id": 0,
                                #     "id": 4383,
                                #     "values": [
                                #         {
                                #             "dictionary_value_id": 0,
                                #             "value": "200"
                                #         }
                                #     ]
                                # },
                                #====================================
                                #is required: False
                                #Материал
                                {
                                    "complex_id": 0,
                                    "id": 7199,
                                    "values": [
                                        {
                                            "dictionary_value_id": 62015,
                                            "value": "Пластик"
                                        }
                                    ]
                                },
                                #========================================
                                #is required: False
                                #Вид техники
                                {
                                    "complex_id": 0,
                                    "id": 7206,
                                    "values": [
                                        {
                                            "dictionary_value_id": 41233,
                                            "value": "Легковые автомобили"
                                        }
                                    ]
                                },
                                #==================================================
                                #is required: False
                                #Место установки
                                {
                                    "complex_id": 0,
                                    "id": 7271,
                                    "values": [
                                        {
                                            "dictionary_value_id": 57641,
                                            "value": "Капот"
                                        }
                                    ]
                                },
                                #============================================
                                #is required: False
                                #Цвет товара
                                {
                                    "complex_id": 0,
                                    "id": 10096,
                                    "values": [
                                        {
                                            "dictionary_value_id": 61574,
                                            "value": "черный"
                                        }
                                    ]
                                },
                                #=======================================================
                                #is required: False
                                #Вид крепления дефлектора
                                {
                                    "complex_id": 0,
                                    "id": 22102,
                                    "values": [
                                        {
                                            "dictionary_value_id": 971313323,
                                            "value": "Накладные"
                                        }
                                    ]
                                },
                                #============================================
                                #is required: False
                                #Вид выпуска товара
                                {
                                    "complex_id": 0,
                                    "id": 22270,
                                    "values": [
                                        {
                                            "dictionary_value_id": 971417785,
                                            "value": "Фабричное производство"
                                        }
                                    ]
                                },
                                #================================================
                                #is required : false
                                #key words
                                {
                                    "complex_id": 0,
                                    "id": 22336,
                                    "values": [
                                        {
                                            "dictionary_value_id": 0,
                                            "value": key_word
                                        }
                                    ]
                                },
                                #==============================================
                                # is required : false
                                # Марка
                                # Укажите марку автомобиля, для которой подходит ваш товар. 
                                # Если товар подходит для нескольких марок, 
                                # то создайте новые комбинации с другими значениями ниже.
                                # {
                                #     "complex_id": 0,
                                #     "id": 22916,
                                #     "values": [
                                #         {
                                #             "dictionary_value_id": vehicle_brand_id,
                                #             "value": vehicle_brand
                                #         }
                                #     ]
                                # },
                                #==============================================
                                # is required : false
                                # Модель
                                # Выберите модель автомобиля, для которой подходит ваш товар, исходя из выбранной марки автомобиля. 
                                # Если товар подходит для нескольких моделей, 
                                # то создайте новые комбинации с другими значениями ниже.
                                # {
                                #     "complex_id": 0,
                                #     "id": 22917,
                                #     "values": [
                                #         {
                                #             "dictionary_value_id": vehicle_model_id,
                                #             "value": vehicle_model
                                #         }
                                #     ]
                                # },
                                 #=====================================
                                #is required: False
                                #Количество, штук
                                {
                                    "complex_id": 0,
                                    "id": 7202,
                                    "values": [
                                        {
                                            "dictionary_value_id": 45536,
                                            "value": "1"
                                        }
                                    ]
                                },

                            ],
                            "barcode":"",
                            "description_category_id": 17028755,
                            "color_image": "",
                            "complex_attributes": [],
                            "currency_code": "RUB",
                            "depth":1000,
                            "dimension_unit": "mm",
                            "height": 30,
                            "images": [str(row.Image_1), str(row.Image_2), str(row.Image_3) ],
                            "images360": [],
                            "name": str(row.Title),
                            "offer_id": str(row.Article),
                            "old_price": str(row.Old_Price),
                            "pdf_list": [],
                            "price": str(row.Retail_Price),
                            "primary_image":str(row.Primary_Image),
                            "type_id": 94656,
                            "vat": "0",
                            "weight": 1000,
                            "weight_unit": "g",
                            "width": 200,
                        }
                    ]
                }
            
            
            elif 'Дефлекторы окон' in row.Title:
                key_word= f"""дефлектор; дефлекторы; дефлектор окна; дефлекторы окон; дефлектор двери; дефлекторы дверей; 
дефлекторы на машину; дефлекторы на двери; {row.Russian_Model}; {row.Russian_Brand}; {row.AutoBrand}; {row.AutoModel}; {row.Russian_Brand} {row.Russian_Model}; {row.AutoBrand} {row.AutoModel}"""

                description_string = f"""Дефлекторы окон - это необходимый аксессуар для любого автомобиля, который помогает защитить ваши окна от грязи и пыли. Они также могут служить дополнительной опцией безопасности, предотвращая попадание мусора внутрь машины.

Дефлекторы окон {row.Model} - это отличный выбор для тех, кто хочет добавить стиль и функциональность своему автомобилю. Эти дефлекторы изготовлены из высококачественного пластика, что обеспечивает их долговечность и прочность.

Дефлекторы окон {row.Model} имеют накладное крепление, которое позволяет легко установить их на любую модель автомобиля. Они подходят как для передних, так и для задних дверей, что делает их универсальными и удобными в использовании.

Дефлекторы окон {row.Model} - это отличный выбор для тех, кто хочет добавить стиль и функциональность своему автомобилю. Они изготовлены из высококачественного пластика, что обеспечивает их долговечность и прочность. Их накладное крепление позволяет легко установить их на любую модель автомобиля, а их универсальность делает их идеальным решением для всех водителей."""            
            
                task = {
                        "items": [
                                {
                                    "attributes": [    
                    
                    #===========================================
                    #is required: True
                    #"Название модели (для объединения в одну карточку)",
                    #"Укажите название модели товара. Не указывайте в этом поле тип и бренд."
                    #Чтобы объединить две карточки, для каждой передайте 9048 в массиве attributes. 
                    #Все атрибуты в этих карточках, кроме размера или цвета, должны совпадать.
                    {
                        "complex_id": 0,
                        "id": 9048,
                        "values": [
                            {
                                "dictionary_value_id": 0,
                                "value": str(row.Model)
                            }
                        ]
                    },
                    #====================================
                    # is required: true
                    # Бренд
                    {
                        "complex_id": 0,
                        "id": 85,
                        "values": [
                            {
                                "dictionary_value_id": 0,
                                "value": "Нет бренда"
                            }
                        ]
                    },
                    #============================================
                    #is requried: False
                    #guarantee period
                    #{
                    #    "complex_id": 0,
                    #    "id": 4385,
                    #    "values": [
                    #        {
                    #           "dictionary_value_id": 0,
                    #            "value": "12 месяцев"
                    #        }
                    #   ]
                    #},
                    #====================================
                    #is required: False
                    #Материал
                    {
                        "complex_id": 0,
                        "id": 7199,
                        "values": [
                            {
                                "dictionary_value_id": 62015,
                                "value": "Пластик"
                            }
                        ]
                    },
                    #============================================
                    #is required: False
                    #Цвет товара
                    {
                        "complex_id": 0,
                        "id": 10096,
                        "values": [
                            {
                                "dictionary_value_id": 61574,
                                "value": "черный"
                            }
                        ]
                    },
                    #=====================================
                    # is required: true
                    # Партномер(article)
                    # Уникальный код (артикул*) однозначно идентифицирующий деталь автомобиля. 
                    # *Маркировка завода-изготовителя автомобиля для OE (оригинальных) запчастей или 
                    # номер детали по каталогу фирмы-производителя для OEM (не оригинальных). 
                    # Если такого артикула у вас нет- продублируйте сюда артикул товара
                    {
                        "complex_id": 0,
                        "id": 7236,
                        "values": [
                            {
                                "dictionary_value_id": 0,
                                "value": article
                            }
                        ]
                    },
                    #=====================================================
                    #is required: false
                    #Название
                    #Название пишется по принципу:\nТип + Бренд + Модель (серия + пояснение) + Артикул производителя + , (запятая) + Атрибут\n
                    # Название не пишется большими буквами (не используем caps lock).\n
                    # Перед атрибутом ставится запятая. Если атрибутов несколько, они так же разделяются запятыми.\n
                    # Если какой-то составной части названия нет - пропускаем её.\n
                    # Атрибутом может быть: цвет, вес, объём, количество штук в упаковке и т.д.\n
                    # Цвет пишется с маленькой буквы, в мужском роде, единственном числе.\n
                    # Слово цвет в названии не пишем.\nТочка в конце не ставится.\n
                    # Никаких знаков препинания, кроме запятой, не используем.\n
                    # Кавычки используем только для названий на русском языке.\n
                    # Примеры корректных названий:\n
                    # Смартфон Apple iPhone XS MT572RU/A, space black \n
                    # Кеды Dr. Martens Киноклассика, бело-черные, размер 43\n
                    # Стиральный порошок Ariel Магия белого с мерной ложкой, 15 кг\n
                    # Соус Heinz Xtreme Tabasco суперострый, 10 мл\n
                    # Игрушка для животных Четыре лапы \"Бегающая мышка\" БММ, белый",
                    {
                        "complex_id": 0,
                        "id": 4180,
                        "values": [
                            {
                                "dictionary_value_id": 0,
                                "value": str(row.Title)
                            }
                        ]
                    },
                    #==========================================================
                    # is required: False
                    # Комплектация
                    # Перечислите, что входит в комплект вместе с товаром
                    {
                        "complex_id": 0,
                        "id": 4384,
                        "values": [
                            {
                                "dictionary_value_id": 0,
                                "value": "Дефлекторы 4 шт., монтажный скотч"
                            }
                        ]
                    },
                    #============================================
                    #is required: False
                    #Вид выпуска товара
                    {
                        "complex_id": 0,
                        "id": 22270,
                        "values": [
                            {
                                "dictionary_value_id": 971417785,
                                "value": "Фабричное производство"
                            }
                        ]
                    },
                    #==================================================
                    #is required: False
                    #Место установки
                    {
                        "complex_id": 0,
                        "id": 7271,
                        "values": [
                            {
                                "dictionary_value_id": 57649,
                                "value": "Передние двери"
                            },
                            {
                                "dictionary_value_id": 57640,
                                "value": "Задние двери"
                            }
                        ]
                    },
                    #==================================================
                    # is required: False
                    # Аннотация
                    # Описание товара, маркетинговый текст. Необходимо заполнять на русском языке
                    {
                        "complex_id": 0,
                        "id": 4191,
                        "values": [
                            {
                                "dictionary_value_id": 0,
                                "value": description_string
                            }
                        ]
                    },
                    #================================================
                    #is required : false
                    #key words
                    {
                        "complex_id": 0,
                        "id": 22336,
                        "values": [
                            {
                                "dictionary_value_id": 0,
                                "value": key_word
                            }
                        ]
                    },
                    #==================================================
                    #is requred: False
                    #Country of manufacture
                    {
                        "complex_id": 0,
                        "id": 4389,
                        "values": [
                            {
                                "dictionary_value_id": 90295,
                                "value": "Россия"
                            }
                        ]
                    },
                    #=======================================================
                    #is required: False
                    #Вид крепления дефлектора
                    {
                        "complex_id": 0,
                        "id": 22102,
                        "values": [
                            {
                                "dictionary_value_id": str(row.Installation_ID),
                                "value": str(row.Installation)
                            }
                        ]
                    },
                    #=======================================
                    # is required: true
                    # Тип
                    {
                        "complex_id": 0,
                        "id": 8229,
                        "values": [
                            {
                                "dictionary_value_id": 97593,
                                "value": "Дефлектор для окон"
                            }
                        ]
                    },
                ],
                        "barcode":"",
                        "description_category_id": 17028755,
                        "color_image": "",
                        "complex_attributes": [],
                        "currency_code": "RUB",
                        "depth":500,
                        "dimension_unit": "mm",
                        "height": 50,
                        "images": [str(row.Image_1), str(row.Image_2), str(row.Image_3), str(row.Image_4), str(row.Image_5) ],
                        "images360": [],
                        "name": str(row.Title),
                        "offer_id": str(row.Article),
                        "old_price": str(row.Old_Price),
                        "pdf_list": [],
                        "price": str(row.Retail_Price),
                        "primary_image":str(row.Primary_Image),
                        "type_id": 97593,
                        "vat": "0",
                        "weight": 1000,
                        "weight_unit": "g",
                        "width": 200,
                    }
                ]
            }

            #uploading new or updating existing product
            response=requests.post('https://api-seller.ozon.ru/v3/product/import', json=task, headers=headers)  
            status_code=response.status_code
            json=response.json()
            print('=========Request Status & Task ID==========================')
            #print('Наименование ' + str(n))
            print(status_code)
            if status_code == 200:
                print('Товар в БД Озон создан')
            else:
                string=f'. Товар {product.id} в БД Озон не создан.'
                print(string)
                messages.error(request,  string)
            print(json)
            #a=json['result']
            task_id=json['result']['task_id']
            print('Task_id: ' + str(task_id))
            # в качестве ответа данный метод возвращает task_id. Мы можем использовать task id 
            #в методе response=requests.post('https://api-seller.ozon.ru/v1/product/import/info', json=task_1, headers=headers)
            #для того, чтобы узнать статус загрузки наименования. Если всё ок, то данный метод должен возвратить ozon_id,
            #но обычно озону нужно время, чтобы отмодерировать новое наименование, поэтому, если сделать запрос сразу,
            # ответ приходит без ozon_id, который нам нужен для загрузки кол-ва.

            # print('===================Status of Task Id=========================')
            # task_1  = {
            #     "task_id": task_id
            # }
            # response=requests.post('https://api-seller.ozon.ru/v1/product/import/info', json=task_1, headers=headers)
            # json=response.json() 
            # print(json)
            # a=json['result']
            # task_id=a['task_id']
            # print('============================================================')
            # print('')
            time.sleep(1.0)
        
        
        
        
        return redirect("dashboard")

def getting_ozon_id_and_ozon_sku (request):
    if request.user.is_authenticated:
        headers = {
                    "Client-Id": "1711314",
                    "Api-Key": 'b54f0a3f-2e1a-4366-807e-165387fb5ba7'
                }
        if request.method == "POST":
            file = request.FILES["file_name"]
            df1 = pandas.read_excel(file)
            cycle = len(df1)
            dict={}
            for i in range(cycle):
                row = df1.iloc[i]#reads each row of the df1 one by one
                article=row.Article
                if '/' in str(article):
                    article=article.replace('/', '_')
                #====================getting rid of extra spaces in the string==================================
                #article=article.replace(' ', '')#getting rid of extra spaces
                #article=article.strip()#getting rid of extra spaces at both sides of the string
                article=article.split()
                article=' '.join(article)
                #============================end of block=======================================================
                if Product.objects.filter(article=article).exists():
                    product=Product.objects.get(article=article)
                    #ozon_id assigned by Ozon for further saving it in erms product model
                    #and using it for changing quantity of product at ozon;
                    #Cуществует два метода получения ozon_id
                    task=    {
                            "filter": {
                                "offer_id": [
                                    article,
                                ],
                            
                                "visibility": "ALL"
                            },
                            "last_id": "",
                            "limit": 100
                        }
                    response=requests.post('https://api-seller.ozon.ru/v3/product/list', json=task, headers=headers) 
                    #print(response)
                    json=response.json()
                    ozon_id=json['result']['items'][0]['product_id']
                    #a=json['result']
                    #print (a)
                    # b=a['items']
                    # print(b)
                    #c=b[0]
                    #print(c)
                    # d=c['product_id']
                    print(ozon_id)
                    product.ozon_id=ozon_id
                    time.sleep(1)
                    #================================
                    task=    {
                        "offer_id": [
                                ],
                        "product_id": [product.ozon_id],
                            "sku": [
                                ]
                        }
                    response=requests.post('https://api-seller.ozon.ru/v3/product/info/list', json=task, headers=headers) 
                    json=response.json()
                    sku_id=json['items'][0]['sources'][0]['sku']
                    # data=json['items']
                    # data=data[0]
                    # data=data['sources']
                    # data=data[0]
                    # sku_id=data['sku']
                    product.ozon_sku=sku_id
                    product.save()
                    time.sleep(1)
                else:
                    dict[row.Article]=row.Title
            string=f'Ozon_id для артикулов {dict} не был сохранен, так как данные артикулы отсутствуют в базе данных'
            messages.error(request, string)
            return redirect("dashboard")

def delivery_auto(request):
    doc_type = DocumentType.objects.get(name="Поступление ТМЦ")
    if request.method == "POST":
        dateTime=request.POST.get('dateTime', False)
        if dateTime:
            # converting dateTime in str format (2021-07-08T01:05) to django format ()
            dateTime = datetime.datetime.strptime(dateTime, "%Y-%m-%dT%H:%M")
            #adding seconds & microseconds to 'dateTime' since it comes as '2021-07-10 01:05:03:00' and we need it real value of seconds & microseconds
            current_dt=datetime.datetime.now()
            mics=current_dt.microsecond
            tdelta_1=datetime.timedelta(microseconds=mics)
            secs=current_dt.second
            tdelta_2=datetime.timedelta(seconds=secs)
            tdelta_3=tdelta_1+tdelta_2
            dateTime=dateTime+tdelta_3
        else:
            tdelta=datetime.timedelta(hours=3)
            dT_utcnow=datetime.datetime.now(tz=pytz.UTC)#Greenwich time aware of timezones
            dateTime=dT_utcnow+tdelta
        file = request.FILES["file_name"]
        headers = {
                    "Client-Id": "1711314",
                        "Api-Key": 'b54f0a3f-2e1a-4366-807e-165387fb5ba7'
                }
        stock_arr=[]
        # print(file)
        # df1 = pandas.read_excel('Delivery_21_06_21.xlsx')
        df1 = pandas.read_excel(file)
        cycle = len(df1)
        dict_new_article={}
        dict_no_ozon_id={}
        for i in range(cycle):
            row = df1.iloc[i]#reads each row of the df1 one by one
            article=str(row.Article)
            if '/' in str(article):
                article=article.replace('/', '_')
            #====================getting rid of extra spaces in the string==================================
            #article=article.replace(' ', '')#getting rid of extra spaces
            #article=article.strip()#getting rid of extra spaces at both sides of the string
            article=article.split()
            article=' '.join(article)

            if Product.objects.filter(article=article).exists():
                product=Product.objects.get(article=article)
                total_qnty = product.quantity + int(row.Qnty)
                total_sum = row.Wholesale_Price * row.Qnty + product.total_sum
                av_price=total_sum / total_qnty
                product.total_sum=total_sum
                product.quantity=total_qnty
                product.av_price=av_price
                product.save()
            
                # checking docs before remainder_history
                if RemainderHistory.objects.filter(article=article, created__lt=dateTime).exists():
                    rho_latest_before = RemainderHistory.objects.filter(article=article,  created__lt=dateTime).latest('created')
                    pre_remainder=rho_latest_before.current_remainder
                else:
                    pre_remainder=0
                # creating remainder_history
                rho = RemainderHistory.objects.create(
                    rho_type=doc_type,
                    created=dateTime,
                    article=article,
                    ozon_id=product.ozon_id,
                    name=product.name,
                    pre_remainder=pre_remainder,
                    incoming_quantity=row.Qnty,
                    outgoing_quantity=0,
                    current_remainder=pre_remainder + int(row.Qnty),
                    wholesale_price=int(row.Wholesale_Price),
                    retail_price=int(row.Retail_Price),
                    total_retail_sum=int(row.Retail_Price) * int(row.Qnty),
                )

                #checking if product already has Ozon_id & does not have to be created again
                if product.ozon_id:
                #Сначала мы создаём новую позицию на площадке озон в функции (def ozon_product_create), которая содержит API метод
                #response=requests.post('https://api-seller.ozon.ru/v3/product/import', json=task, headers=headers)
                #мы не можем сразу ввести количество на маркетплейсе Ozon, так как ему требуется время для модерации

                #В процессе содания нового товара Ozon присваивает ему уникальный product_id
                #Мы получаем product_id посредством метода: response=requests.post('https://api-seller.ozon.ru/v3/product/list', 
                # json=task, headers=headers) (def getting_ozon_id) и сохраняем ozon_id в модели Product в поле ozon_id

                #Ozon_id и offer_id нужны для редактирования количества товара на стоке озон посредством метода:
                #response=requests.post('https://api-seller.ozon.ru/v2/products/stocks', json=task_3, headers=headers)
                #offer_id это номер товара уникальный в erms. В качестве offer_id мы используем артикул товара.

                #я пытался создать товар и задать ему количество в одной функции, но Озону нужно время для того, чтобы проверить,
                #что я создал у него на площадке, и он возвращает нужныйм нам ozon_id только через какое-то время, а не сразу
                #поэтому я разделил процесс создания товара на озоне, получения ozon_id и ввода кол-ва на озон на три отдельных функции
                #Сначала мы создаем товар (def ozon_product_create), а 
                #Затем получаем ozon_id (def getting_ozon_id)
                #Вводим документ (def deliver_auto), где загружаем поступившее кол-во товара на ООС и одновременно на озон

                
                    stock_dict={
                                "offer_id": str(product.article),
                                "product_id": str(product.ozon_id),
                                "stock": rho.current_remainder,
                                #warehouse (Неклюдово)
                                "warehouse_id": 1020005000113280
                            }
                    stock_arr.append(stock_dict)
                   
            
                    #update quantity of products at ozon warehouse making it equal to OOC warehouse
                    # task = {
                    #     "stocks": [
                    #         {
                    #             "offer_id": str(product.article),
                    #             "product_id": str(product.ozon_id),
                    #             "stock": rho.current_remainder,
                    #             #warehouse (Неклюдово)
                    #             "warehouse_id": 1020005000113280
                    #         }
                    #     ]
                    # }
                else:
                    dict_no_ozon_id[row.Article]=row.Title
            else:
                dict_new_article[row.Article]=row.Title

        task={
            "stocks" : stock_arr
        }
        response=requests.post('https://api-seller.ozon.ru/v2/products/stocks', json=task, headers=headers)
        print(response)
        json=response.json()
        #print(status_code)
        print(json)
                
            
        print('=============================')        
        print('No product with this article:')        
        for key, value in  dict_new_article.items():
            print(str(key) +' : '+ str(value))
        print('=============================')        
        print('Product with no ozon_id:') 
        for key, value in  dict_no_ozon_id.items():
            print(str(key) +' : ' +str(value))

        return redirect("dashboard")

def zero_ozon_qnty(request):
    #if request.method == "POST":
    category=ProductCategory.objects.get(name='Дефлектор капота')
    products=Product.objects.filter(category=category)
    headers = {
                "Client-Id": "1711314",
                "Api-Key": 'b54f0a3f-2e1a-4366-807e-165387fb5ba7'
            }
    for product in products:
                   
        #update quantity of products at ozon warehouse making it equal to OOC warehouse
        task = {
            "stocks": [
                {
                    "offer_id": str(product.article),
                    "product_id": str(product.ozon_id),
                    "stock": 0,
                    #warehouse (Неклюдово)
                    "warehouse_id": 1020005000113280
                }
            ]
        }
        response=requests.post('https://api-seller.ozon.ru/v2/products/stocks', json=task, headers=headers)
        time.sleep(1)
        # print(response)
        # json=response.json()
        #print(status_code)
        # print(json)

    return redirect("dashboard")

#for both ozon & wb
def synchronize_qnty(request):
    tdelta=datetime.timedelta(hours=3)
    dT_utcnow=datetime.datetime.now(tz=pytz.UTC)#Greenwich time aware of timezones
    dateTime=dT_utcnow+tdelta
    if request.method == "POST":
        headers = {
                        "Client-Id": "1711314",
                        "Api-Key": 'b54f0a3f-2e1a-4366-807e-165387fb5ba7'
                    }
        stock_arr=[]
        category = request.POST["category"]
        category=ProductCategory.objects.get(id=category)
        products=Product.objects.filter(category=category)
        for product in products:
            article=product.article
            if RemainderHistory.objects.filter(article=article).exists():
                #rhos=RemainderHistory.objects.filter(article=article)
                rho_latest = RemainderHistory.objects.filter(article=article, created__lte=dateTime).latest("created")
               
                if product.ozon_id:
                    stock_dict={
                        "offer_id": str(product.article),
                        "product_id": str(product.ozon_id),
                        "stock": rho_latest.current_remainder,
                        #warehouse (Неклюдово)
                        "warehouse_id": 1020005000113280
                    }
                    stock_arr.append(stock_dict)
        #update quantity of products at ozon warehouse making it equal to OOC warehouse
        #За один запрос можно изменить наличие для 100 товаров. 
        #С одного аккаунта продавца можно отправить до 80 запросов в минуту.
        #в настоящий момент в каждой категории товара менее 100 позиций, поэтому проблем не возникает, но
        #с увеличением кол-ва более 100 нужно будет менять код
        task={
            "stocks" : stock_arr
        }
        response=requests.post('https://api-seller.ozon.ru/v2/products/stocks', json=task, headers=headers)
        status_code=response.status_code
        print(status_code)
        #print(response)
        json=response.json()
        print(json)
        #time.sleep(1)
            
                # if product.wb_bar_code:
                #     warehouseId=1368124
                #     url=f'https://marketplace-api.wildberries.ru/api/v3/stocks/{warehouseId}'
                #     headers = {"Authorization": "eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjUwMjE3djEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTc2MDM0Nzg4NywiaWQiOiIwMTk2MzExMC04MmJiLTdjMGEtYTEzYy03MjdmMjY5NzVjZWEiLCJpaWQiOjEwMjIxMDYwMCwib2lkIjo0MjQ1NTQ1LCJzIjo3OTM0LCJzaWQiOiJkZDQ2MDQ1Mi03NWQzLTQ0OTktOWU4OC1jMjVhNTE1NzBhNzIiLCJ0IjpmYWxzZSwidWlkIjoxMDIyMTA2MDB9.srXrKwyCJCH_nZAzKi4PaT6pueamPhwz-hqBYP7l--UafAd0gmNTSr7xoNWxFmN1S65kG-2WBUA_l0qrYaDGvg"}
                #     wb_bar_code=str(product.wb_bar_code)
                #     qnty=rho_latest.current_remainder
                #     # print('======================')
                #     # print(wb_bar_code)
                #     # print(rho_latest.current_remainder)
                #     params= {
                #         "stocks": [
                #         {
                #             "sku": wb_bar_code,#WB Barcode
                #             "amount": qnty,
                #         }
                #         ]
                #     }
                #     response = requests.put(url, json=params, headers=headers)
                #     #status_code=response.status_code
                #     #Status Code: 204 No Content
                #     #There is no content to send for this request except for headers.
                #     time.sleep(1)
    return redirect ('dashboard')

def update_prices(request):
    if request.user.is_authenticated:
        headers = {
                    "Client-Id": "1711314",
                    "Api-Key": 'b54f0a3f-2e1a-4366-807e-165387fb5ba7'
                }
        if request.method == "POST":
            file = request.FILES["file_name"]
            df1 = pandas.read_excel(file)
            cycle = len(df1)
            dict_new_article={}
            for i in range(cycle):
                row = df1.iloc[i]#reads each row of the df1 one by one
                article=row.Article
                if '/' in str(article):
                    article=article.replace('/', '_')
                #====================getting rid of extra spaces in the string==================================
                #article=article.replace(' ', '')#getting rid of extra spaces
                #article=article.strip()#getting rid of extra spaces at both sides of the string
                article=article.split()
                article=' '.join(article)
                #============================end of block=======================================================


                if Product.objects.filter(article=article).exists():
                    product=Product.objects.get(article=article)
                
                    task=    {
                        "prices": [
                            {
                            "auto_action_enabled": "UNKNOWN",
                            "auto_add_to_ozon_actions_list_enabled": "UNKNOWN",
                            "currency_code": "RUB",
                            "min_price": str(row.Min_Price),
                            "min_price_for_auto_actions_enabled": True,
                            "net_price": str(row.Wholesale_Price),
                            "offer_id": "",
                            "old_price": str(row.Old_Price),
                            "price": str(row.Retail_Price),
                            "price_strategy_enabled": "UNKNOWN",
                            "product_id": product.ozon_id,
                            "quant_size": 1,
                            "vat": '0'
                            }
                        ]
                    }
                    response=requests.post('https://api-seller.ozon.ru/v1/product/import/prices', json=task, headers=headers) 
                    print(response)
                    json=response.json()
                    print(json)
                    print('============================')      
                    time.sleep(1)
                else:
                    dict_new_article[row.Article]=row.Title

            length=len(dict_new_article)
            if length>0:
                string=f'Ozon_id для артикулов {dict_new_article} не был сохранен, так как данные артикулы отсутствуют в базе данных'
                messages.error(request, string)
                return redirect("dashboard")
            else:
                return redirect ('dashboard')    
           
    else:
        return redirect ('dashboard')

def update_images(request):
    headers = {
                "Client-Id": "1711314",
                "Api-Key": 'b54f0a3f-2e1a-4366-807e-165387fb5ba7'
            }
    if request.method == "POST":
        file = request.FILES["file_name"]
        df1 = pandas.read_excel(file)
        cycle = len(df1)
        for i in range(cycle):
            row = df1.iloc[i]#reads each row of the df1 one by one
            article=row.Article
            if '/' in str(article):
                article=article.replace('/', '_')
            #====================getting rid of extra spaces in the string==================================
            #article=article.replace(' ', '')#getting rid of extra spaces
            #article=article.strip()#getting rid of extra spaces at both sides of the string
            article=article.split()
            article=' '.join(article)
            #============================end of block=======================================================  
            product=Product.objects.get(article=row.Article)
            task = {
                "color_image": "string",
                "images": [
                    str(row.Primary_Image),
                    str(row.Image_1),
                    str(row.Image_2),
                    #str(row.Image_3)
                ],
                "images360": [
                    "string"
                ],
                "product_id": product.ozon_id
            }
            response=requests.post('https://api-seller.ozon.ru/v1/product/pictures/import', json=task, headers=headers) 
            print(response)
            json=response.json()
            print(json)
            print('============================')      
            time.sleep(1)
        return redirect ('dashboard')

#does not send any info to ozon
def sale (request):
    doc_type = DocumentType.objects.get(name="Продажа ТМЦ")
    if request.method == "POST":
        dateTime=request.POST.get('dateTime', False)
        if dateTime:
            # converting dateTime in str format (2021-07-08T01:05) to django format ()
            dateTime = datetime.datetime.strptime(dateTime, "%Y-%m-%dT%H:%M")
            #adding seconds & microseconds to 'dateTime' since it comes as '2021-07-10 01:05:03:00' and we need it real value of seconds & microseconds
            current_dt=datetime.datetime.now()
            mics=current_dt.microsecond
            tdelta_1=datetime.timedelta(microseconds=mics)
            secs=current_dt.second
            tdelta_2=datetime.timedelta(seconds=secs)
            tdelta_3=tdelta_1+tdelta_2
            dateTime=dateTime+tdelta_3
        else:
            tdelta=datetime.timedelta(hours=3)
            dT_utcnow=datetime.datetime.now(tz=pytz.UTC)#Greenwich time aware of timezones
            dateTime=dT_utcnow+tdelta
        article = request.POST["article"]

        #====================getting rid of extra spaces in the string==================================
        #article=article.replace(' ', '')#getting rid of extra spaces
        #article=article.strip()#getting rid of extra spaces at both sides of the string
        article=article.split()
        article=' '.join(article)
        #============================end of block=======================================================
        retail_price = request.POST["retail_price"]
        retail_price=int(retail_price)
        if Product.objects.filter(article=article).exists():
            product=Product.objects.get(article=article)
            total_qnty = product.quantity - 1
            if total_qnty >=0:
                total_sum=product.total_sum-product.av_price
                product.quantity=total_qnty
                product.total_sum=total_sum
                product.save()
            else:
                messages.error(request,"Документ не проведен. Недостаточное кол-во товара на остатке")
                return redirect("dashboard")
        else:
            messages.error(request,"Документ не проведен. Товар с таким артикулом не сущствует")
            return redirect("dashboard")
          # checking docs before remainder_history
        if RemainderHistory.objects.filter(article=article, created__lt=dateTime).exists():
            rho_latest_before = RemainderHistory.objects.filter(article=article,  created__lt=dateTime).latest('created')
            pre_remainder=rho_latest_before.current_remainder
        else:
            pre_remainder=0
        # creating remainder_history
        rho = RemainderHistory.objects.create(
            rho_type=doc_type,
            created=dateTime,
            article=article,
            ozon_id=product.ozon_id,
            name=product.name,
            pre_remainder=pre_remainder,
            incoming_quantity=0,
            outgoing_quantity=1,
            current_remainder=pre_remainder - 1,
            retail_price=int(retail_price),
            # total_retail_sum=int(row.Retail_Price) * int(row.Qnty),
        )
   
    return redirect ('dashboard')

def recognition (request):
    pass

def return_product (request):
    pass

def general_report (request):
    products=Product.objects.all()
    report_identifier = Identifier.objects.create()
    tdelta=datetime.timedelta(hours=3)
    dT_utcnow=datetime.datetime.now(tz=pytz.UTC)#Greenwich time aware of timezones
    dateTime=dT_utcnow+tdelta
    for product in products:
        article=product.article
        if RemainderHistory.objects.filter(article=article).exists():
            rhos=RemainderHistory.objects.filter(article=article)
            rho_latest = RemainderHistory.objects.filter(article=article, created__lte=dateTime).latest("created")
            rho_earliest = RemainderHistory.objects.filter(article=article, created__lte=dateTime).earliest("created")
            current_remainder=rho_latest.current_remainder
            pre_remainder=rho_earliest.pre_remainder
            incoming_quantity=0
            outgoing_quantity=0
            for rho in rhos:
                incoming_quantity+=rho.incoming_quantity
                outgoing_quantity+=rho.outgoing_quantity
            report=Report.objects.create(
                identifier=report_identifier,
                article=article,
                name=rho.name,
                pre_remainder=pre_remainder,
                incoming_quantity=incoming_quantity,
                outgoing_quantity=outgoing_quantity,
                current_remainder=current_remainder,
                av_price=product.av_price
            )
             
    #=======================Uploading to Excel Module===================================
    response = HttpResponse(content_type="application/ms-excel")
    response["Content-Disposition"] = (
        "attachment; filename=Remainder_" + str(datetime.date.today()) + ".xls"
    )

    wb = xlwt.Workbook(encoding="utf-8")
    ws = wb.add_sheet("Remainder")

    # sheet header in the first row
    row_num = 0
    font_style = xlwt.XFStyle()

    columns = ["Article", "Title","Av_price", "Pre_remainder", "Incoming_Qnty", 'Outgoing_Qnty', 'Current_Remainder']
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # sheet body, remaining rows
    font_style = xlwt.XFStyle()
    report_query = Report.objects.filter(identifier=report_identifier)
    query = report_query.values_list("article", "name",'av_price', "pre_remainder",  "incoming_quantity", 'outgoing_quantity', 'current_remainder' )

    for row in query:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, str(row[col_num]), font_style)
    wb.save(response)
    return response
#=======================End of Excel Upload Module================================


#=================================WB Functions==============================
def wb_create_product (request):
    url=f'https://content-api.wildberries.ru/content/v2/cards/upload'
    headers = {"Authorization": "eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjUwMjE3djEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTc2MDM0Nzg4NywiaWQiOiIwMTk2MzExMC04MmJiLTdjMGEtYTEzYy03MjdmMjY5NzVjZWEiLCJpaWQiOjEwMjIxMDYwMCwib2lkIjo0MjQ1NTQ1LCJzIjo3OTM0LCJzaWQiOiJkZDQ2MDQ1Mi03NWQzLTQ0OTktOWU4OC1jMjVhNTE1NzBhNzIiLCJ0IjpmYWxzZSwidWlkIjoxMDIyMTA2MDB9.srXrKwyCJCH_nZAzKi4PaT6pueamPhwz-hqBYP7l--UafAd0gmNTSr7xoNWxFmN1S65kG-2WBUA_l0qrYaDGvg"}
    params=[]
    if request.method == "POST":
        file = request.FILES["file_name"]
        df1 = pandas.read_excel(file)
        cycle = len(df1)
        for i in range(cycle):
            row = df1.iloc[i]#reads each row of the df1 one by one
            article=row.Article
            if '/' in str(article):
                article=article.replace('/', '_')
            category=row.Category
            #====================getting rid of extra spaces in the string==================================
            #category=category.replace(' ', '')#getting rid of extra spaces
            #category=category.strip()#getting rid of extra spaces at both sides of the string
            category=category.split()
            category=' '.join(category)
            #============================end of block=======================================================
            #====================getting rid of extra spaces in the string==================================
            #article=article.replace(' ', '')#getting rid of extra spaces
            #article=article.strip()#getting rid of extra spaces at both sides of the string
            article=article.split()
            article=' '.join(article)
            #============================end of block=======================================================
            category=ProductCategory.objects.get(name=category)
            if Product.objects.filter(article=article).exists():
                product=Product.objects.get(article=article)
                product.name=row.Title
                product.save()
            else:
                product = Product.objects.create(
                    name=row.Title,
                    article=article, #without extra spaces
                    auto_model=row.Model, 
                    category=category    
                )


            if category=="Дефлектор двери":
                description_string = f"""Дефлекторы окон - это необходимый аксессуар для любого автомобиля, который помогает защитить ваши окна от грязи и пыли. Они также могут служить дополнительной опцией безопасности, предотвращая попадание мусора внутрь машины.

Дефлекторы окон {row.Model} - это отличный выбор для тех, кто хочет добавить стиль и функциональность своему автомобилю. Эти дефлекторы изготовлены из высококачественного пластика, что обеспечивает их долговечность и прочность.

Дефлекторы окон {row.Model} имеют накладное крепление, которое позволяет легко установить их на любую модель автомобиля. Они подходят как для передних, так и для задних дверей, что делает их универсальными и удобными в использовании.

Дефлекторы окон {row.Model} - это отличный выбор для тех, кто хочет добавить стиль и функциональность своему автомобилю. Они изготовлены из высококачественного пластика, что обеспечивает их долговечность и прочность. Их накладное крепление позволяет легко установить их на любую модель автомобиля, а их универсальность делает их идеальным решением для всех водителей.""" 
                item={
                    "subjectID": 2251,
                        "variants": [
                        {
                            "vendorCode": article,
                            "title": str(row.Title),
                            "description": description_string,
                            "brand": "Delta Avto",
                            "dimensions": 
                            {
                                "length": 90,
                                "width": 20,
                                "height": 5,
                                "weightBrutto": 1
                            },
                        

                        "characteristics": [
                            {
                                "id": 5023,
                                "value": str(row.AutoModel)
                            },
                            {
                                "id": 16532,
                                "name" : str(row.AutoBrand)
                            },
                            {
                                "id": 17596,
                                "name" : 'пластик'
                            },
                            {
                                "id": 74242,
                                "name" : 'окна'
                            },
                            {
                                "id": 90702,
                                "name" : '4'
                            },
                            {
                                "id": 378533,
                                "name" : 'Дефлекторы (4 шт.), инструкция'
                            },
                            {
                                "id": 5522881,
                                "name" : str(row.Article)
                            },
                            {
                                "id": 14177451,
                                "name" : 'Россия'
                            },
                        ],
                        # "sizes": [
                        #   {
                        #   "techSize": "M",
                        #   "wbSize": "42",
                        #   "price": 2500,
                        #   "skus": []
                        #   }
                        # ]
                        }
                    ]
                    
                }
                params.append(item)

                # params = [
                #     {
                #         "subjectID": 2251,
                #         "variants": [
                #         {
                #             "vendorCode": article,
                #             "title": str(row.Title),
                #             "description": description_string,
                #             "brand": "Delta Avto",
                #             "dimensions": 
                #             {
                #                 "length": 90,
                #                 "width": 20,
                #                 "height": 5,
                #                 "weightBrutto": 1
                #             },
                        

                #         "characteristics": [
                #             {
                #                 "id": 5023,
                #                 "value": str(row.AutoModel)
                #             },
                #             {
                #                 "id": 16532,
                #                 "name" : str(row.AutoBrand)
                #             },
                #             {
                #                 "id": 17596,
                #                 "name" : 'пластик'
                #             },
                #             {
                #                 "id": 74242,
                #                 "name" : 'окна'
                #             },
                #             {
                #                 "id": 90702,
                #                 "name" : '4'
                #             },
                #             {
                #                 "id": 378533,
                #                 "name" : 'Дефлекторы (4 шт.), инструкция'
                #             },
                #             {
                #                 "id": 5522881,
                #                 "name" : str(row.Article)
                #             },
                #             {
                #                 "id": 14177451,
                #                 "name" : 'Россия'
                #             },
                #         ],
                #         # "sizes": [
                #         #   {
                #         #   "techSize": "M",
                #         #   "wbSize": "42",
                #         #   "price": 2500,
                #         #   "skus": []
                #         #   }
                #         # ]
                #         }
                #     ]
                #     }
                # ]

            elif category == "Дефлектор капота":
                description_string = f"""Дефлектор капота (мухобойка) разработан специально для {product.auto_model} ({row.Russian_Brand} {row.Russian_Model}), выполнен из гибкого оргстекла, представляет собой тонкую, просчитанную пластину.

Устанавливается на капот при помощи креплений, которые идут в комплекте, в штатные места в усилителе капота вашего автомобиля.

Расстояние между капотом и дефлектором примерно равно 1 см, оно продувается и промывается на мойке.

Дефлектор защищает фронтальную часть капота от повреждений и царапин. Он отражает камни и песок от впереди идущих машин, сохраняя лакокрасочное покрытие капота целым. Также дефлектор изменяет воздушный поток, уменьшает загрязнение лобового стекла и щёток стеклоочистителя.

В быту дефлектор капота еще называют отбойник или мухобойка, так как помимо камешков он отражает и летящих навстречу машине насекомых.

Цвет дефлектора капота тёмный, тонированный до 20%, на машине он будет выглядеть полностью чёрным. Дефлектор - это не только функциональный атрибут, но и стильный элемент тюнинга, который выгодно выделит на фоне других ваше авто."""
                
                item={
                    "subjectID": 2251,
                        "variants": [
                        {
                            "vendorCode": article,
                            "title": str(row.Title),
                            "description": description_string,
                            "brand": "Delta Avto",
                            "dimensions": 
                            {
                                "length": 100,
                                "width": 30,
                                "height": 5,
                                "weightBrutto": 1
                            },
                        

                        "characteristics": [
                            {
                                "id": 5023,
                                "value": str(row.AutoModel)
                            },
                            {
                                "id": 16532,
                                "name" : str(row.AutoBrand)
                            },
                            {
                                "id": 17596,
                                "name" : 'пластик'
                            },
                            {
                                "id": 74242,
                                "name" : 'капот'
                            },
                            {
                                "id": 90702,
                                "name" : '3'
                            },
                            {
                                "id": 378533,
                                "name" : 'Дефлектор (1 шт.), крепеж, инструкция'
                            },
                            {
                                "id": 5522881,
                                "name" : str(row.Article)
                            },
                            {
                                "id": 14177451,
                                "name" : 'Россия'
                            },
                        ],
                        # "sizes": [
                        #   {
                        #   "techSize": "M",
                        #   "wbSize": "42",
                        #   "price": 2500,
                        #   "skus": []
                        #   }
                        # ]
                        }
                    ]
                    
                }
                params.append(item)

        #Максимум 10 запросов в минуту на один аккаунт продавца
        #В одном запросе можно создать максимум 100 объединённых карточек товаров (imtID), по 30 карточек товаров в каждой. Максимальный размер запроса 10 Мб.
        response = requests.post(url, json=params, headers=headers)
        status_code=response.status_code
        a=response.json()
        print(f'status_code: {status_code}')
        print(a)
        # b=a['data']
        # for i in b:
        #   print(i)
         
    
    messages.error(request,f'WB Response: {a}')
    return redirect ('dashboard')

def wb_add_media_files (request):
  if request.method == "POST":
    file = request.FILES["file_name"]
    df1 = pandas.read_excel(file)
    cycle = len(df1)
    for i in range(cycle):
      row = df1.iloc[i]#reads each row of the df1 one by one
      article=row.Article
      if '/' in str(article):
          article=article.replace('/', '_')

      if Product.objects.filter(article=article).exists():
        product=Product.objects.get(article=article)
        print('====================')
        if product.wb_id:
            wb_id=product.wb_id
            print(product.wb_id)
            print(product.image_1)
            image_1='https://mp-system.ru/media/' + str(product.image_1)
            url=f'https://content-api.wildberries.ru/content/v3/media/save'
            headers = {"Authorization": "eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjUwMjE3djEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTc2MDM0Nzg4NywiaWQiOiIwMTk2MzExMC04MmJiLTdjMGEtYTEzYy03MjdmMjY5NzVjZWEiLCJpaWQiOjEwMjIxMDYwMCwib2lkIjo0MjQ1NTQ1LCJzIjo3OTM0LCJzaWQiOiJkZDQ2MDQ1Mi03NWQzLTQ0OTktOWU4OC1jMjVhNTE1NzBhNzIiLCJ0IjpmYWxzZSwidWlkIjoxMDIyMTA2MDB9.srXrKwyCJCH_nZAzKi4PaT6pueamPhwz-hqBYP7l--UafAd0gmNTSr7xoNWxFmN1S65kG-2WBUA_l0qrYaDGvg"}
            params = {
                "nmId": int(wb_id),
                #"nmId": 447408585,
                "data": [
                    image_1,
                    "https://mp-system.ru/media/uploads/DeflectorDoor_im_2.jpg",
                    "https://mp-system.ru/media/uploads/DeflectorDoor_im_3.jpg",
                    "https://mp-system.ru/media/uploads/DeflectorDoor_im_4.jpg",
                    "https://mp-system.ru/media/uploads/DeflectorDoor_im_5.jpg",
                    "https://mp-system.ru/media/uploads/DeflectorDoor_im_6.jpg"
                ]
            }

            response = requests.post(url, json=params, headers=headers)
            status_code=response.status_code
            a=response.json()
            print(f'status_code: {status_code}')
            print(a)
            time.sleep(1)
  messages.error(request,f'WB Response: {a}')
  return redirect ('dashboard')

#getting wb id & saving it in Product model
def wb_get_id (request):
  url=f'https://content-api.wildberries.ru/content/v2/get/cards/list'
  headers = {"Authorization": "eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjUwMjE3djEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTc2MDM0Nzg4NywiaWQiOiIwMTk2MzExMC04MmJiLTdjMGEtYTEzYy03MjdmMjY5NzVjZWEiLCJpaWQiOjEwMjIxMDYwMCwib2lkIjo0MjQ1NTQ1LCJzIjo3OTM0LCJzaWQiOiJkZDQ2MDQ1Mi03NWQzLTQ0OTktOWU4OC1jMjVhNTE1NzBhNzIiLCJ0IjpmYWxzZSwidWlkIjoxMDIyMTA2MDB9.srXrKwyCJCH_nZAzKi4PaT6pueamPhwz-hqBYP7l--UafAd0gmNTSr7xoNWxFmN1S65kG-2WBUA_l0qrYaDGvg"}

  params = {
        "settings": {
              "sort": {
                  "ascending": False
                  },
              "filter": {
                  "withPhoto": -1
              },
              "cursor": {
                'limit':100
              }


        }
  }

  response = requests.post(url, json=params, headers=headers)
  status_code=response.status_code
  a=response.json()
  print(f'status_code: {status_code}')
  a=a['cards']

  for i in a:
    wb_id=i['nmID']
    wb_bar_code=i['sizes'][0]['skus'][0]
    article=i['vendorCode']
    print(article)
    if Product.objects.filter(article=article).exists():
      product=Product.objects.get(article=article)
      product.wb_id=wb_id
      product.wb_bar_code=wb_bar_code
      product.save()
      print(f'{product.name} : {product.article} : {product.wb_id} : {product.wb_id}')
      print('======================')
      time.sleep(1)

      # messages.error(request,f'WB Product: {product.name} : {product.article} : {product.wb_id}')
  return redirect ('dashboard')

def wb_update_prices(request):
    #Товары, цены и скидки для них. Максимум 1 000 товаров. Цена и скидка не могут быть пустыми одновременно.
	#Максимум 10 запросов за 6 секунд для всех методов категории Цены и скидки на один аккаунт продавца
    url=f'https://discounts-prices-api.wildberries.ru/api/v2/upload/task'
    headers = {"Authorization": "eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjUwMjE3djEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTc2MDM0Nzg4NywiaWQiOiIwMTk2MzExMC04MmJiLTdjMGEtYTEzYy03MjdmMjY5NzVjZWEiLCJpaWQiOjEwMjIxMDYwMCwib2lkIjo0MjQ1NTQ1LCJzIjo3OTM0LCJzaWQiOiJkZDQ2MDQ1Mi03NWQzLTQ0OTktOWU4OC1jMjVhNTE1NzBhNzIiLCJ0IjpmYWxzZSwidWlkIjoxMDIyMTA2MDB9.srXrKwyCJCH_nZAzKi4PaT6pueamPhwz-hqBYP7l--UafAd0gmNTSr7xoNWxFmN1S65kG-2WBUA_l0qrYaDGvg"}
    if request.method == "POST":
        file = request.FILES["file_name"]
        df1 = pandas.read_excel(file)
        cycle = len(df1)
        task_arr=[]
        for i in range(cycle):
            row = df1.iloc[i]#reads each row of the df1 one by one
            article=row.Article
            retail_price=row.Retail_Price

            if '/' in str(article):
                article=article.replace('/', '_')
            #====================getting rid of extra spaces in the string==================================
            #article=article.replace(' ', '')#getting rid of extra spaces
            #article=article.strip()#getting rid of extra spaces at both sides of the string
            article=article.split()
            article=' '.join(article)
            #============================end of block=======================================================

            if Product.objects.filter(article=article).exists():
                product=Product.objects.get(article=article)
                if product.wb_id:
                    wb_id=product.wb_id
                    task_dict={
                            "nmID": int(wb_id),
                            # "price": int(retail_price),
                            "price": 2990,
                            "discount": 0
                        }
                    task_arr.append(task_dict)


                    # params={
                    #         "data": [
                    #             {
                    #             "nmID": int(wb_id),
                    #             # "price": int(retail_price),
                    #             "price": 2990,
                    #             "discount": 0
                    #             }
                    #         ]
                    #     }
            
            params={
                "data" : task_arr
            }
            response = requests.post(url, json=params, headers=headers)
            status_code=response.status_code
            a=response.json()
            print(f'status_code: {status_code}')
            print(a)
            messages.error(request,f'WB Response: {a}')

        return redirect ('dashboard')
    

def wb_update_prices_ver_1(request):
    #Товары, цены и скидки для них. Максимум 1 000 товаров. Цена и скидка не могут быть пустыми одновременно.
	#Максимум 10 запросов за 6 секунд для всех методов категории Цены и скидки на один аккаунт продавца
    url=f'https://discounts-prices-api.wildberries.ru/api/v2/upload/task'
    headers = {"Authorization": "eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjUwMjE3djEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTc2MDM0Nzg4NywiaWQiOiIwMTk2MzExMC04MmJiLTdjMGEtYTEzYy03MjdmMjY5NzVjZWEiLCJpaWQiOjEwMjIxMDYwMCwib2lkIjo0MjQ1NTQ1LCJzIjo3OTM0LCJzaWQiOiJkZDQ2MDQ1Mi03NWQzLTQ0OTktOWU4OC1jMjVhNTE1NzBhNzIiLCJ0IjpmYWxzZSwidWlkIjoxMDIyMTA2MDB9.srXrKwyCJCH_nZAzKi4PaT6pueamPhwz-hqBYP7l--UafAd0gmNTSr7xoNWxFmN1S65kG-2WBUA_l0qrYaDGvg"}
    task_arr=[]
    products=Product.objects.all()
    for product in products:
        if product.wb_id:
            wb_id=product.wb_id
            task_dict={
                    "nmID": int(wb_id),
                    # "price": int(retail_price),
                    "price": 2990,
                    "discount": 0
                }
            task_arr.append(task_dict)
  
    params={
        "data" : task_arr
    }
    response = requests.post(url, json=params, headers=headers)
    status_code=response.status_code
    a=response.json()
    print(f'status_code: {status_code}')
    print(a)
    messages.error(request,f'WB Response: {a}')

    return redirect ('dashboard')