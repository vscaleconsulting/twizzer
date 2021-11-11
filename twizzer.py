import tweepy
import gspread
import requests
import time


class VscaleTwitterBot():
  
  def __init__(self,gc_credential_file_name,spreadsheet_url
               ,tweepy_consumer_key,tweepy_consumer_secret,
               tweepy_callback_uri):
    
    '''
      gc -> auth to service account 
      spreadsheet_url -> spread sheet url
      tweepy_credentials -> dict of tweepy credentials containing consumer_key,secret_key,callback_uri 
    '''
    self.tweet_links = []
    self.result_worksheet = None #result worksheet object
    self.scraped_till = 2
    
    self.spreadsheet_url = spreadsheet_url
    self.gc = gspread.service_account(filename=gc_credential_file_name)
    self.tweepy_credentials = {
      'consumer_key':tweepy_consumer_key,
      'consumer_secret_key':tweepy_consumer_secret,
      'callback_url':tweepy_callback_uri
    } 
  
  

  # return tweepy api obj
  def get_api(self)->object:

    '''
        takes tweepy credentials and return api object for tweepy api calls    
    '''
    
    consumer_key = self.tweepy_credentials['consumer_key']
    consumer_secret = self.tweepy_credentials['consumer_secret_key']
    callback_uri = self.tweepy_credentials['callback_url']

    auth = tweepy.OAuthHandler(consumer_key,consumer_secret,callback=callback_uri)

    return tweepy.API(auth)



  def get_tweet_info(self,tweet_id)->dict:  

    '''
      returns scrapped dict and influencer status id of given tweet status id.
      else error-> returns empty empty dict and None 
    '''

    try:
      api = self.get_api()
      tweet = api.get_status(tweet_id)._json
      influencer_status_id = tweet["in_reply_to_status_id_str"]

      

      tweet_out = [
            f"https://twitter.com/{tweet['user']['screen_name']}",
            f"https://twitter.com/{tweet['user']['screen_name']}/status/{tweet_id}",
            tweet['favorite_count'],
            tweet['text'],
      ]
        
      return tweet_out,influencer_status_id

    except:
      #no data available for curr url
      return [],None    




  def binder(self,link)->dict:
    
    '''
      binder-> binds info of both promoter and influencer and returns result dictonary
    '''
    
    tweet_id = link.split("/")[-1].split("?")[0] #get tweet id
    
    promoter_info,influencer_tweet_id = self.get_tweet_info(tweet_id)
    influencer_info,garbage = self.get_tweet_info(influencer_tweet_id)
    
    
    return promoter_info + influencer_info
    
    
  def get_spreadsheet(self)->None:
    
    '''
      fills instance variables with spreadsheet tweetlinks and  result_worksheet with worksheet[1] object
    '''
    gsheet = self.gc.open_by_url(self.spreadsheet_url)
    spreadsheet_response = gsheet.values_get(f"Form Responses 1!E{self.scraped_till}:E")
    
    if 'values' in spreadsheet_response:        
      self.scraped_till += len(spreadsheet_response)-1
      self.tweet_links = spreadsheet_response['values']
      self.result_worksheet = gsheet.worksheets()[1]    
      return 
      
    return "no values"
    
  def scrape_tweets(self):    
   
    if(self.get_spreadsheet()=="no values"): #fetch sheets to instance variables
      print("no new values appended")
      return 
    
    api_call_counts = 0
    try:
      for link in self.tweet_links[:9]:
        scrapped_values = self.binder(link[0])
        # print(scrapped_values)
        self.result_worksheet.append_row(scrapped_values)
      
        if api_call_counts==900:
          time.sleep(910) #api call limit run after every 15min as per my research
          api_call_counts = 0 # reset counter

        elif api_call_counts%10==0:
          time.sleep(2) #10 req per sec 
        
        api_call_counts+=1
        
    except Exception as e:
      print(e,"exception froms scrape tweets method")
    
    return  
    
  def run_twizzer(self):
    
    while True:
      self.scrape_tweets()
      time.sleep(15)
    
    
     
   
consumer_key = "hvJ3Mc5hfuw6FbuW0GwsrNail"
consumer_secret = "77g1My9L2oEyzY137okPsRAlB2hOjkLulyxZRJ00lbVMY8NKwe"
callback_uri = "oob"
        
spredsheet_url = "https://docs.google.com/spreadsheets/d/1PoAJO-u_WQKgPWO478rduiss6ooYMqitqxdE-LZzJkc/edit?usp=sharing"
bot = VscaleTwitterBot("twizzer/cred.json",spredsheet_url,consumer_key,consumer_secret,callback_uri)        

bot.run_twizzer()
   





