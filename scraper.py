import os 
import scrapy
import time
class LawPhil(scrapy.Spider):
    name = 'lawphil_spider'
    basepath = "https://lawphil.net/judjuris"
    yearlinks = []
    monthlinks = []
    bydaylinks = []

    curdir = os.getcwd()
    def start_requests(self):
        yield scrapy.Request("https://lawphil.net/judjuris/judjuris.html", self.parse_year_links)
        # yield scrapy.Request("https://lawphil.net/judjuris/juri2021/nov2021/gr_239746_2021.html", self.testparse)

    def testparse(self, response):
        textcontent = response.css('blockquote ::text').getall()
        testfile = "".join(list(textcontent))
        
        with open("testfile.txt", 'w', encoding='utf8', errors='ignore') as f:
            testfile = testfile.replace(" ", " ")
            testfile = testfile.replace("­", " ")
            testfile = testfile.replace("The Lawphil Project - Arellano Law Foundation","")
            f.write(testfile)


    def parse_year_links(self, response):
        self.yearlinks = response.css('td a.off_n1 ::attr(href)').getall()
        print(self.yearlinks)
        for yearlink in self.yearlinks[0:1]:
            yeartoparse = "%s/%s"% (self.basepath,yearlink)
            yearcat, yearpage = yearlink.split("/")
            juri, year = yearcat.split('juri')
            datafolder = "%s/data/%s" % (self.curdir,year)
            if not os.path.exists(datafolder):
                os.makedirs(datafolder) 
            yield scrapy.Request(yeartoparse, self.parse_month_links, cb_kwargs={'year':year})

    def parse_month_links(self, response, year=None):
        if not year is None:
            self.monthlinks = response.css('td a.off ::attr(href)').getall()
            for monthlink in self.monthlinks[0:1]:
                monthcat, monthpage = monthlink.split("/")
                month, ynum = monthcat.split(year)
                monthdatafolder = "%s/data/%s/%s" % (self.curdir, year, month)
                if not os.path.exists(monthdatafolder):
                    os.makedirs(monthdatafolder)
                monthtoparse = "%s/juri%s/%s"% (self.basepath,year,monthlink)
                yield scrapy.Request(monthtoparse, self.parse_byday_links, cb_kwargs={'year':year,'month':month})

    def parse_byday_links(self, response,year=None,month=None):
        if not year is None and not month is None:
            self.bydaylinks = response.css('td a ::attr(href)').getall()
            for bydaylink in self.bydaylinks[0:1]:
                bdayname = bydaylink
                linkispdf = False
                if 'pdf' in bydaylink:
                    pdft, bdayname = bydaylink.split('/')
                    linkispdf =True
                bdayname, bext = bdayname.split('.')
                filepathfolder = "%s/data/%s/%s/%s"% (self.curdir,year,month,bdayname)
                filelink = "%s/juri%s/%s%s/%s" % (self.basepath,year,month,year,bydaylink)
                if not os.path.exists(filepathfolder):
                    os.makedirs(filepathfolder)
                if linkispdf:
                    yield scrapy.Request(filelink, self.save_pdf, cb_kwargs={'fname':bdayname,'fpath': filepathfolder})
                else:
                    yield scrapy.Request(filelink, self.parse_byday_text, cb_kwargs={'fname':bdayname,'fpath': filepathfolder})

    def parse_byday_text(self, response, fname=None, fpath=None):
        if not fpath is None and not fname is None:
            textcontent = response.css('blockquote ::text').getall()
            texttowrite = "".join(list(textcontent))
            texttowrite = texttowrite.replace(" ", " ")
            texttowrite = texttowrite.replace("­", " ")
            texttowrite = texttowrite.replace("The Lawphil Project - Arellano Law Foundation","")
            savepath = "%s/%s.txt" % (fpath,fname)
            self.logger.info('Saving Text to %s', savepath)

            with open(savepath, 'w', encoding='utf8', errors='ignore') as f:
                f.write(texttowrite)
                time.sleep(1)

    def save_pdf(self, response, fname=None, fpath=None):
        if not fpath is None and not fname is None:
            savepath = "%s/%s.pdf" % (fpath,fname)
            self.logger.info('Saving PDF to %s', savepath)
            with open(savepath, 'wb') as f:
                f.write(response.body)
                time.sleep(1)

