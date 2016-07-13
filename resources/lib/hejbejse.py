# -*- coding: UTF-8 -*-
#/*
# *      Copyright (C) 2011 Ivo Brhel
# *
# *
# *  This Program is free software; you can redistribute it and/or modify
# *  it under the terms of the GNU General Public License as published by
# *  the Free Software Foundation; either version 2, or (at your option)
# *  any later version.
# *
# *  This Program is distributed in the hope that it will be useful,
# *  but WITHOUT ANY WARRANTY; without even the implied warranty of
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# *  GNU General Public License for more details.
# *
# *  You should have received a copy of the GNU General Public License
# *  along with this program; see the file COPYING.  If not, write to
# *  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# *  http://www.gnu.org/copyleft/gpl.html
# *
# */

import re,os,urllib,urllib2,cookielib
import util,resolver

from provider import ContentProvider

class HejbejseContentProvider(ContentProvider):
	
	def __init__(self,username=None,password=None,filter=None):
		ContentProvider.__init__(self,'hejbejse.tv','http://www.kynychova-tv.cz/',username,password,filter)
		opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.LWPCookieJar()))
		urllib2.install_opener(opener)

	def capabilities(self):
		return ['resolve','categories','list']
		
	def categories(self):
		page = util.parse_html('http://www.kynychova-tv.cz/index.php?id=5')
		result = []
		for title,uri in [(x.h3.text,x.h3.a['href']) for x in page.select('div.entry5') if x.h3]:
			item = self.dir_item()
			item['title'] = title
			item['url'] = uri
			result.append(item)
		return result

	def list(self, url):
		url = self._url(url)
		page = util.parse_html(url)
		result = []
		for title,uri in [(x.img['title'],x['href']) for x in page.select('div.entry3')[0].findAll('a')]:
			item = self.video_item()
			item['title'] = title
			item['url'] = uri
			result.append(item)
		return result
	
	def resolve(self,item,captcha_cb=None,select_cb=None):
		item = item.copy()
		url = self._url(item['url'])
		page = util.parse_html(url)
		result = []
		data=str(page.select('div.entry3 > center')[0])
		resolved = resolver.findstreams(data,['<iframe(.+?)src=[\"\'](?P<url>.+?)[\'\"]'])
		try:
			for i in resolved:
				item = self.video_item()
				item['title'] = i['name']
				item['url'] = i['url']
				item['quality'] = i['quality']
				item['surl'] = i['surl']
				result.append(item)	 
		except:
			print '===Unknown resolver==='
			
		if len(result)==1:
			return result[0]
		elif len(result) > 1 and select_cb:
			return select_cb(result)
