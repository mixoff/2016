# 2016
Coding Competition 2016


## Identify Service
POST to https://mixoff-identity-test.eu-gb.mybluemix.net/identify

With a body of
{
	"name":"kevin bacon",
	"url" : "http://blogs.longwood.edu/jameslaycock/files/2015/03/19_Kevin_Bacon.jpg"
}


## Analysis Service
POST to https://mixoff-identity-test.eu-gb.mybluemix.net/analyse

With a body of:
{
	"name":"kevin bacon",
	"url" : "http://blogs.longwood.edu/jameslaycock/files/2015/03/19_Kevin_Bacon.jpg"
}

or

{
	"name":"ak47",
	"url" : "http://www.no2star.com/file/2016/09/AKAGUN02leftD.jpg"
}

https://mixoff-identity-test.eu-gb.mybluemix.net/image  
Defaults to kevin. It shows where the face is and the name of the person if it recognises it. Also shows the category (e.g. 'person') at the top corner

https://mixoff-identity-test.eu-gb.mybluemix.net/image?url=http://cp91279.biography.com/1000509261001/1000509261001_1086612957001_Bio-Biography-Britney-Spears-LF1.jpg

Works with objects too (limited to 2MB)

can now POST an image to https://mixoff-identity-test.eu-gb.mybluemix.net/pic to get it displayed. Remember to set the content-type
