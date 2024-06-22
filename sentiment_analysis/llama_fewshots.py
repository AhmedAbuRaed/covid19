from sys import argv

from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch
import json

output_file_path, tweets_file_path, lama_2_folder_path = argv[1:]

# Define the path for the output and input files
# output_path = '/scratch/st-carenini-1/covid19/llama_tweets_canada_en_0_output_sent.txt'
# tweets_path = '/scratch/st-carenini-1/covid19/tweets_canada_en_0.txt'
# output_path = 'D:/Research/UBC/covid19/canada_output_sent.txt'
# tweets_path = 'D:/Research/UBC/covid19/tweets_canada_en_0.txt'
output_path = output_file_path
tweets_path = tweets_file_path

# Update to the LLaMA 2 model path or identifier
# lama_2_model_path = "/arc/project/st-carenini-1/LLMs/huggingface/llama-2-13b-chat-hf"
# lama_2_model_path = "D:/Research/UBC/llama/llama-2-13b-hf"
lama_2_model_path = lama_2_folder_path

tokenizer = AutoTokenizer.from_pretrained(lama_2_model_path)
model = AutoModelForCausalLM.from_pretrained(lama_2_model_path)

text_gen_pipeline = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    torch_dtype=torch.bfloat16,
    device_map="auto",
)

# Few-shot examples with multiple aspects per tweet
few_shot_examples = [
    {"Tweet #": 1, "Region-month": "Can-Dec", "Tweet": "@EXPSGamble Thanks Ryan😂 I’m thinking w common sense. You know what will affect kids Susan! This crap Masks Isolation No school No bdays No grads Home with their abuser No sports. Increased weight gainThat’s long Covid.Wake a reporter U should be asking", "Aspect": "isolation", "Sentiment": "negative"},
    {"Tweet #": 2, "Region-month": "Can-Dec", "Tweet": "Long COVID is the new Chronic Fatigue Syndrome. In other words, a fake disease #COVID19", "Aspect": "Long COVID", "Sentiment": "negative"},
    {"Tweet #": 2, "Region-month": "Can-Dec", "Tweet": "Long COVID is the new Chronic Fatigue Syndrome. In other words, a fake disease #COVID19", "Aspect": "Chronic Fatigue Syndrome", "Sentiment": "negative"},
    {"Tweet #": 3, "Region-month": "Can-Dec", "Tweet": "All #postviral disease are the very definition of complex chronic illness & here in Canada we have no supports. 25 years disabled & I hunted high and low, & can say this with certainty. The worst element for that is myalgic encephalitis #TreatLongCovid #pwME #treatpostviral", "Aspect": "myalgic encephalitis", "Sentiment": "negative"},
    {"Tweet #": 4, "Region-month": "Can-Dec", "Tweet": "@DeansKevin @DoctorsWithME Thank you! I hope more doctors will follow your lead and learn about #MEcfs.", "Aspect": "doctors", "Sentiment": "positive"},
    {"Tweet #": 5, "Region-month": "Can-Dec", "Tweet": "@SarahPema: “My heart goes out to anyone dealing with this illness. #MECFS is a silent assassin and it’s vicious. It has a cruel propens…", "Aspect": "#MECFS", "Sentiment": "negative"},
    {"Tweet #": 6, "Region-month": "Can-Dec", "Tweet": "@j_b_kennedy @miffythegamer Have tou tried Ivermectin? Has worked to resolve long covid for many. The FLCCC have effective treatment protocols for doctors on their site.", "Aspect": "ivermectin", "Sentiment": "positive"},
    {"Tweet #": 7, "Region-month": "Can-Jan", "Tweet": "The clinics will be staffed with specialists and health professionals with an extensive knowledge of the virus long-haulers, the province said. I'm glad this is happening, but I'm skeptical that a bunch of BC specialists in post-viral illnesses have magically materialized!", "Aspect": "specialists", "Sentiment": "negative"},
    {"Tweet #": 7, "Region-month": "Can-Jan", "Tweet": "The clinics will be staffed with specialists and health professionals with an extensive knowledge of the virus long-haulers, the province said. I'm glad this is happening, but I'm skeptical that a bunch of BC specialists in post-viral illnesses have magically materialized!", "Aspect": "health professionals", "Sentiment": "neutral"},
    {"Tweet #": 8, "Region-month": "Can-Jan", "Tweet": "@CBCCalgary: 60% of COVID-19 long-haulers say government is 'absolutely ignoring them,' Marketplace questionnaire finds", "Aspect": "government", "Sentiment": "negative"},
    {"Tweet #": 9, "Region-month": "Can-Jan", "Tweet": "@CMOH_Alberta Goes both ways. Long haulers are tired of being gaslit (that’s a form of abuse if you didn’t know) by health providers. We are NOT recovered. We are NOT being dramatic. Can you please educate them on post *covid* syndrome? Or do you not know about it yet either?", "Aspect": "health providers", "Sentiment": "negative"},
    {"Tweet #": 10, "Region-month": "Can-Jan", "Tweet": "@dianaberrent: 'They're absolutely ignoring us': COVID-19 long-haulers plead for help from federal and provincial governments", "Aspect": "governments", "Sentiment": "negative"},
    {"Tweet #": 11, "Region-month": "Can-Jan", "Tweet": "@Limbictweets Very #MECFS #longhaulers expected this Our experts have warned the wider community for the past *year* that merely staying alive through the initial infection is not a guarantee you'll be fine #MasksSaveLives in more ways than avoiding death", "Aspect": "masks", "Sentiment": "positive"},
    {"Tweet #": 12, "Region-month": "Can-Jan", "Tweet": "@syramadad: Long haul COVID19 or those suffering lingering illness and *long* term symptoms following infection is a public health crisis…", "Aspect": "public health", "Sentiment": "neutral"},
    {"Tweet #": 13, "Region-month": "Can-Jan", "Tweet": "More reason to seriously protect *children* from #Covid19 - even asymptomatic resulting in Type 1 diabetes. The #LongCovid effects are quickly becoming a chronic public health nightmare #CDNpoli #BCpoli #BCed", "Aspect": "public health", "Sentiment": "neutral"},
    {"Tweet #": 14, "Region-month": "US-Aug", "Tweet": "Key word “willful” #LongCovid was predictable. Why downplay? 1) Ignorance: Permanent LT effects documented after every pandemic & infection yet Health officials thought #COVID19 would be 1st virus not to 2) Arrogance: Didn’t know so doesn’t exist 3) Negligence: They always knew", "Aspect": "health officials", "Sentiment": "negative"},
    {"Tweet #": 15, "Region-month": "US-Aug", "Tweet": "@icant3000 @Connardanonyme1 Now that yearlong isolation, followed by the willful sabotage of Hot Vax Summer, have made me depressed, do I have Long Covid?", "Aspect": "isolation", "Sentiment": "negative"},
    {"Tweet #": 16, "Region-month": "US-Jul", "Tweet": "@TanglerBOB @dennisnagpal1 The mRNA vaccine is a very clever way to produce a vaccine, but in the end it essentially works the same as any other: your B cells produce antibodies against a part of the virus. There will be no weird long-term effects, unlike", "Aspect": "mRNA", "Sentiment": "neutral"},
    {"Tweet #": 17, "Region-month": "US-May", "Tweet": "@Survivor_Corps @AFLCIO @DanCGoldberg Millions of people could develop long Covid. But there is no clear diagnosis for it, let alone a cure. Many patients say they're being gaslit by physicians, told their symptoms are all in their head, especially if they got ", "Aspect": "physicians", "Sentiment": "negative"},
    {"Tweet #": 18, "Region-month": "US-May", "Tweet": "Physicians who reduce the complicated and frightening experience of sick patients to a diagnosis of “well, you’re fat” should lose all their patients. Lazy prick tells Covid long haulers with destroyed lungs it’s about their BMI and I hope I never need a doctor as long as I live.", "Aspect": "physicians", "Sentiment": "negative"},
    {"Tweet #": 19, "Region-month": "US-Nov", "Tweet": "@CanYouSpellmRNA @jusstinray @MarcusBeam1 @mjjmk04 @AConcernedPare2 @8bitpath @TwoQuoque Long COVID is mostly BS. It’s a combination of regular old Post Viral Syndrome and hypochondria", "Aspect": "Long COVID", "Sentiment": "negative"},
    {"Tweet #": 20, "Region-month": "US-Nov", "Tweet": "@DonitaJose: Mr Suresh survived a horrific post-covid / long Covid episode for 6 months at Gandhi Hospital. He fell ill in April this year…", "Aspect": "Long COVID", "Sentiment": "negative"},
    {"Tweet #": 21, "Region-month": "US-Nov", "Tweet": "@comradecumslut This is awful. Is there a different clinic you could try? I’m finally healing a bit and I do think it’s thanks to my long Covid clinic doctor! I’m in the US though.", "Aspect": "doctors", "Sentiment": "positive"},
    {"Tweet #": 22, "Region-month": "US-Nov", "Tweet": "You don't want to get #COVID19 & you _really_ don't want to get #LongCOVID. #VaccinesSaveLives", "Aspect": "vaccine", "Sentiment": "positive"},
    {"Tweet #": 22, "Region-month": "US-Nov", "Tweet": "You don't want to get #COVID19 & you _really_ don't want to get #LongCOVID. #VaccinesSaveLives", "Aspect": "masks", "Sentiment": "negative"},
    {"Tweet #": 23, "Region-month": "US-Nov", "Tweet": "@marcelloup @TruthSeekingHCP @JustinTrudeau @GovCanHealth Corrupt pharma told you about long Covid and you blindly accept it. Perhaps if we didn’t stuff kids with processed foods, medication and vaccines they’ll be healthier and won’t have issues like ast", "Aspect": "medication", "Sentiment": "negative"},
    {"Tweet #": 23, "Region-month": "US-Nov", "Tweet": "@marcelloup @TruthSeekingHCP @JustinTrudeau @GovCanHealth Corrupt pharma told you about long Covid and you blindly accept it. Perhaps if we didn’t stuff kids with processed foods, medication and vaccines they’ll be healthier and won’t have issues like ast", "Aspect": "vaccines", "Sentiment": "negative"},
    {"Tweet #": 24, "Region-month": "Can-Jan", "Tweet": "@DrFrancesRyan: This is absolutely chilling. If you have Long Covid, please understand *many* doctors are ignorant of post-viral fatigue a…", "Aspect": "doctors", "Sentiment": "negative"},
    {"Tweet #": 25, "Region-month": "Can-Jan", "Tweet": "@DJignyte @EastSceptic @iandaisyfox @ParkinJim @KatyMcconkey @GazWatty1 @InCytometry @cjsnowdon @FatEmperor @malmphegor @janexrj @steakandliver @braidedmanga @70s_70sgirl @NickStripe_ONS 1. Lockdowns don’t work. 2. The vaccine only decreases symptoms - no evidence that it will impact *long* Covid. 3. Long Covid is not new and not as prevalent as you may think.", "Aspect": "lockdowns", "Sentiment": "neutral"},
    {"Tweet #": 25, "Region-month": "Can-Jan", "Tweet": "@DJignyte @EastSceptic @iandaisyfox @ParkinJim @KatyMcconkey @GazWatty1 @InCytometry @cjsnowdon @FatEmperor @malmphegor @janexrj @steakandliver @braidedmanga @70s_70sgirl @NickStripe_ONS 1. Lockdowns don’t work. 2. The vaccine only decreases symptoms - no evidence that it will impact *long* Covid. 3. Long Covid is not new and not as prevalent as you may think.", "Aspect": "vaccine", "Sentiment": "neutral"},
    {"Tweet #": 26, "Region-month": "Can-Jan", "Tweet": "@PremierScottMoe I’m pretty sure Sk has similar graphics, but this one from today’s Edm Sun clearly shows why the restrictions are essential for long-term COVID success. Lifting restrictions until vaccines are widely distributed is the WRONG strategy", "Aspect": "restrictions", "Sentiment": "positive"},
    {"Tweet #": 27, "Region-month": "US-Nov", "Tweet": "@DrTomFrieden Unvaccinated people are at the highest risk of developing long-term physical and mental damage from Covid, Perhaps, because they already have mental damage. We have a safe and effective vaccine. Reduce your risk of getting long Covid—get vac", "Aspect": "vaccine", "Sentiment": "positive"},
    {"Tweet #": 28, "Region-month": "Can-Jan", "Tweet": "...several ME/CFS experts told me that they anticipate a wave of new patients — long-haulers who, because their symptoms are severe enough and last for 6 months or longer, will essentially be ME/CFS patients whether they receive the diagnosis or not.", "Aspect": "experts", "Sentiment": "neutral"},
    {"Tweet #": 28, "Region-month": "Can-Jan", "Tweet": "...several ME/CFS experts told me that they anticipate a wave of new patients — long-haulers who, because their symptoms are severe enough and last for 6 months or longer, will essentially be ME/CFS patients whether they receive the diagnosis or not.", "Aspect": "ME/CFS", "Sentiment": "neutral"},
    {"Tweet #": 37, "Region-month": "Can-Jan", "Tweet": "As noted, up to 10% of patients recovering from COVID infection seem to experience prolonged symptoms that appear to resemble PVFS or CFS (subset 3). Clinicians may recall that both fatigue syndromes have connections to prior infectious disease outbreaks.", "Aspect": "PVFS", "Sentiment": "neutral"},
    {"Tweet #": 37, "Region-month": "Can-Jan", "Tweet": "As noted, up to 10% of patients recovering from COVID infection seem to experience prolonged symptoms that appear to resemble PVFS or CFS (subset 3). Clinicians may recall that both fatigue syndromes have connections to prior infectious disease outbreaks.", "Aspect": "CFS", "Sentiment": "neutral"},
    {"Tweet #": 38, "Region-month": "Can-Jan", "Tweet": "Specialists have argued that Covid-19 could trigger a second pandemic of CFS/ME.... ‘If well-funded research had begun into CFS/ ME half a century ago, we’d be in a very different situation now with *long* Covid,’ argues Dr Ben Marsh @UKWomensHealth", "Aspect": "research", "Sentiment": "neutral"},
    {"Tweet #": 39, "Region-month": "Can-Jan", "Tweet": "@CBCEdmonton Ivermectin. Why is everyone not talking about this cheap & effective prophylaxis AND treatment (including long-haulers) for Covid-19? Remdesivir (which barely works & only in very narrow circumstances) was shouted from rooftops, wth??", "Aspect": "ivermectin", "Sentiment": "positive"},
    {"Tweet #": 40, "Region-month": "Can-Jan", "Tweet": "@CBCNews COVID long-haulers appear to experience the exact symptoms the ME/CFS *people* experience - post viral symptoms. No surprise they aren't receiving any help. Canada sadly lags behind and medical assistance not pro-active but reactive.", "Aspect": "Canada", "Sentiment": "negative"},
    {"Tweet #": 41, "Region-month": "Can-Jan", "Tweet": "@DrGurdeepParhar: Seniors suffering from total isolation in B.C. care homes with months-long COVID-19 outbreaks, families say", "Aspect": "isolation", "Sentiment": "negative"},
    {"Tweet #": 42, "Region-month": "Can-Jan", "Tweet": "A segment of those infected [w/COVID-19] are living with lasting impacts on their brain health, and we need to know why. Former McGill Alumni Assc. board president Inez Jabalpurwala on why Canada should lead research on long-haul COVID-19 effects, 1/", "Aspect": "research", "Sentiment": "neutral"},
    {"Tweet #": 43, "Region-month": "Can-Jan", "Tweet": "@whittle_jac @jonniker @kreillyweiss @gallopingcats @BFlynnP More people will get long COVID waiting for an MRNA vaccine than if we can halve the *time* to blanket vaccine coverage with the J&J in the mix.", "Aspect": "mRNA", "Sentiment": "neutral"},
    {"Tweet #": 44, "Region-month": "Can-Dec", "Tweet": "@eff_hey It’s weird and extremely telling how the long covid discourse is just about being hypervigilant and moralistic about one super virus instead of about recognising how common and debilitating post-viral fatigue can be", "Aspect": "post-viral fatigue", "Sentiment": "negative"}
]


# Function to convert few-shot examples to a formatted string
def few_shot_to_string(examples):
    header = "Tweet #\tTweet\tAspect\tSentiment"
    formatted_examples = [header] + [
        f"{ex['Tweet #']}\t{ex['Tweet']}\t{ex['Aspect']}\t{ex['Sentiment']}" for ex in examples]
    return "\n".join(formatted_examples)


# Convert few-shot examples to string
few_shot_string = few_shot_to_string(few_shot_examples)


# Function to process and analyze a single tweet
def process_tweet(tweet, pipeline, few_shot_string):
    tweet_text = tweet['text']
    prompt = 'Please analyze the following few shot examples: \n\"' + few_shot_string.replace(r'\n', "") + '\".\n' + '. Now based on the few shot examples, please provide the aspects and their sentiments in json format (dictionary) after applying aspect-based sentiment analysis on the following tweet: \"' + tweet_text.strip().replace(r'\n', "") + "\" Please only return the json string and nothing else."
    try:
        sequences = pipeline(
            prompt,
            max_length=3500,
            do_sample=True,
            top_k=1,
            num_return_sequences=1,
        )
        generated_text = sequences[0]['generated_text']

        # Directly include the generated text as a single result in the list
        results = [generated_text.strip()]

        return results[0]  # Return the single result string
    except Exception as e:
        print(f"Error processing tweet ID {tweet['id']}: {e}")
        return None


# Read tweets and process them
with open(tweets_path, 'r') as rf, open(output_path, 'a') as output:
    for line in rf:
        try:
            data_json = json.loads(line)
            tweet_id = data_json['id']
            created_at = data_json['created_at']
            tweet_text = data_json['text']
            tweet = {'id': tweet_id, 'created_at': created_at, 'text': tweet_text}

            # Process the tweet
            result = process_tweet(tweet, text_gen_pipeline, few_shot_string)
            if result:
                # Write the single result to the output file
                output.write("*TID*:" + tweet_id + "\n" + str(result) + '\n')  # Add a newline for better separation

        except json.JSONDecodeError as e:
            print(f"Error reading line: {e}")
