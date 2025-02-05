def get_email_prompt(first_name, first_line=None, insights=None, language="EN", headline="", category=None):
    """
    Generates a personalized email prompt based on the provided inputs.

    Args:
        first_name (str): The recipient's first name.
        first_line (str, optional): The first-line fact from LinkedIn.
        insights (str, optional): Insights from the company website.
        language (str): The language of the email ("EN" or "NL").
        headline (str, optional): A headline to guide the email.

    Returns:
        str: The email prompt.
    """
    if language == "NL":
        print(category)
        if category == "accomplishment":
            opener = f"gefeliciteerd met {first_line}!"
            example = "gefeliciteerd met {het behalen van iets}!"

        elif category == "informative":
            opener = f"Ik zag je post over {first_line}, mooie inzichten!"
            example = "Ik zag je post over {informatieve post}, mooie inzichten!"

        elif category == "lesson":
            opener = f"Je verhaal over (kort dit gedeelte in:){first_line} op linkedin was interessant. Mooie inzichten!"
            example = "Je verhaal over {gegeven les} op linkedin was interessant. Mooie inzichten!"

        elif category == "milestone":
            opener = f"Gefeliciteerd aan jou en je team met {first_line}—top gedaan!"
            example = "Gefeliciteerd aan jou en je team met {behaalde mijlpaal}—top gedaan!"
        else:
            opener = f"Ik zag dat je je bezig houdt met {headline}"
            example = "Ik zag dat je je bezig houdt met {beroep}"
        opening_line = "Schrijf een openingszin gebaseerd op: " + opener
        sys_message = (
            "Je bent een behulpzame assistent die gespecialiseerd is in het schrijven van e-mails voor Everyman AI. "
            "Mijn naam is Luuk Alleman. De e-mail moet direct gestuurd kunnen worden, dus gebruik NOOIT placeholders. "
            "Schrijf alleen de aanhef en body van de e-mail en schrijf nooit de titel erbij, deze bedenken wij zelf. "
            "Eindig met 'Met vriendelijke groeten,' en voeg hierna absoluut nooit wat extra's toe. "
            "Wees straight to the point en gebruik geen overdreven woorden."
            "Schrijf de mail altijd volledig in het nederlands."
            f"""Voorbeeld van hoe de e-mail geschreven moet worden:

            Hi {first_name},

            **Introductie:**  
            Begin met een specifieke opmerking of compliment over het bedrijf. Verwijs naar iets wat je op hun website hebt gezien, zoals een recent project, dienst of product. In dit geval zat dat over {opener} gaan.

            **Hoofdtekst:**  
            Beschrijf kort 1 tot 3 manieren waarop AI relevant zou kunnen zijn voor hun organisatie. Gebruik duidelijke, eenvoudige taal zonder te technisch te worden.

            Voorbeeld:  
            We hebben jullie website bekeken en dachten aan een aantal manieren waarop AI mogelijk kan bijdragen aan verbetering:  
            1. **Automatiseer klantensupport:** Integreer AI in jullie ticketingsysteem om snel en accuraat supportvragen te beantwoorden.  
            2. **Optimaliseer interne processen:** Automatiseer belangrijke workflows om efficiëntie te verhogen en bottlenecks te verminderen.  
            3. **Versterk jullie product:** Voeg AI-functionaliteiten toe die de waarde en ervaring voor klanten verbeteren.

            **Call-to-Action (CTA):**  
            Nodig de ontvanger uit om een kort gesprek in te plannen. Vermijd termen zoals "100% gratis" en gebruik een vriendelijke, niet-opdringerige toon.  
            Bijvoorbeeld:  
            "Zou je openstaan voor een kort gesprek om te bespreken hoe AI je bedrijfsdoelen kan ondersteunen? Je kunt hier een tijdslot boeken: [Plan een gesprek-link]."

            **Credibiliteit:**  
            Optioneel: Vermeld maximaal 2 relevante resultaten of voorbeelden van andere klanten.  
            Bijvoorbeeld:  
            - _Onze klanten zagen een 23% reductie in operationele kosten en een 19% stijging in productiviteit._
            • 32,5% Betere besluitvorming
            • 23,2% Minder operationele kosten
            • 18,6% Hogere productiviteit en kwaliteit
            • 11,6% Minder impact door menselijke fouten
            • 6,9% Meer omzet
            • 6,9% Nauwkeurigere voorspellingen
            
            **Afsluiting:**  
            Sluit af met een vriendelijke uitnodiging om contact op te nemen of vragen te stellen.

            Voorbeeld e-mailoutput:

            ---

            Hi {first_name},

            Ik zag op jullie website dat jullie bezig zijn met [specifiek project of dienst], wat erg interessant is! Mooi om te zien dat jullie focussen op [relevant onderwerp].

            We hebben gekeken naar hoe AI jullie mogelijk kan helpen en dachten aan het volgende:  
            1. **Automatiseer klantensupport:** AI kan veelvoorkomende vragen snel en nauwkeurig afhandelen.  
            2. **Optimaliseer interne processen:** Verbeter de efficiëntie door automatisering van kernprocessen.  
            3. **Verhoog de klantwaarde:** Voeg AI-functionaliteiten toe om klanten een betere ervaring te bieden.

            Zou je het interessant vinden om hierover van gedachten te wisselen in een kort gesprek? Je kunt hier een tijdslot boeken: [Plan een gesprek].

            Ik hoor graag van je. Als je vragen hebt, kun je me altijd bereiken via deze e-mail.

            Met vriendelijke groeten, """
            "Schrijf goede HTML opmaak die we direct naar de lead door kunnen sturen, gebruik geen kleuren tekst in de HTML, zorg ervoor dat de layout van de email goed is, gebruik whitespaces etc zodat dit goed leesbaar is."
        )
        if first_line and insights:
            return f"""
            Je bent een expert in het schrijven van professionele e-mails. Schrijf een zeer gepersonaliseerde cold e-mail aan {first_name} met deze headline: {headline}.
            
            Gebruik direct het volgende feitje gebaseerd op een linkedin post van deze persoon. Dit is dus iets wat zij zelf gezegd hebben en wij willen dit benoemen als een pakkende opener maar wees niet te uitgebreid, het is een nonchalante opener die in 1 zin geschreven moet worden in zeer simpele taal: {opening_line}.
            
            som de analyse van de bedrijfswebsite op om hun interesse te wekken zonder in al teveel detail te treden, we willen alleen laten zien dat we research hebben gedaan en ideeen hebben: {insights}
            
            Het doel is om een connectie te maken en AI-ontwikkeling diensten aan te bieden door een 30 minuut durende call. 
            Dit kan ingepland worden via de volgende link: https://calendar.app.google/bC1TedkCNRgYd3aB6.
            
            Voeg aan het einde van de e-mail een zin toe dat er altijd talloze mooie ideeën voortkomen uit een brainstorm over AI-projecten, en dat dit het vrijwel altijd waard is.
            Schrijf de e-mail in HTML-formaat zodat deze correct weergegeven wordt in e-mailclients. Zorg voor duidelijke paragrafen, witregels en een professionele uitstraling.
            Sluit af met "Met vriendelijke groeten," zonder extra toevoegingen.
            """, sys_message
        elif insights:
            return f"""
            Je bent een expert in het schrijven van professionele e-mails. Schrijf een zeer gepersonaliseerde cold e-mail aan {first_name} met deze headline: {headline}.
            
            Start de mail direct met een scherpe observatie gebaseerd op de volgende analyse van de bedrijfswebsite en maak daarna een korte opsomming van deze analyse om hun interesse te wekken zonder in al teveel detail te treden: {insights}.
            
            Het doel is om een connectie te maken en AI-ontwikkeling diensten aan te bieden door een 30 minuut durende call. 
            Dit kan ingepland worden via de volgende link: https://calendar.app.google/bC1TedkCNRgYd3aB6.
            
            Voeg aan het einde van de e-mail een zin toe dat er altijd talloze mooie ideeën voortkomen uit een brainstorm over AI-projecten, en dat dit het vrijwel altijd waard is.
            Schrijf de e-mail in HTML-formaat zodat deze correct weergegeven wordt in e-mailclients. Zorg voor duidelijke paragrafen, witregels en een professionele uitstraling.
            Sluit af met "Met vriendelijke groeten," zonder extra toevoegingen.
            """, sys_message
        elif first_line:
            return f"""
            Je bent een expert in het schrijven van professionele e-mails. Schrijf een zeer gepersonaliseerde cold e-mail aan {first_name} met deze headline: {headline}.
            
            Gebruik direct het volgende feitje gebaseerd op een linkedin post van deze persoon. Dit is dus iets wat zij zelf gezegd hebben en wij willen dit benoemen als een pakkende opener maar wees niet te uitgebreid, het is een nonchalante opener die in 1 zin geschreven moet worden in zeer simpele taal: {opening_line}.
            
            Het doel is om een connectie te maken en AI-ontwikkeling diensten aan te bieden door een 30 minuut durende call. 
            Dit kan ingepland worden via de volgende link: https://calendar.app.google/bC1TedkCNRgYd3aB6.
            
            Voeg aan het einde van de e-mail een zin toe dat er altijd talloze mooie ideeën voortkomen uit een brainstorm over AI-projecten, en dat dit het vrijwel altijd waard is.
            Schrijf de e-mail in HTML-formaat zodat deze correct weergegeven wordt in e-mailclients. Zorg voor duidelijke paragrafen, witregels en een professionele uitstraling.
            Sluit af met "Met vriendelijke groeten," zonder extra toevoegingen.
            """, sys_message
        else:
            return f"""
            Je bent een expert in het schrijven van professionele e-mails. Schrijf een zeer gepersonaliseerde cold e-mail aan {first_name} met deze headline: {headline}.
                        
            Het doel is om een connectie te maken en AI-ontwikkeling diensten aan te bieden door een 30 minuut durende call. 
            Dit kan ingepland worden via de volgende link: https://calendar.app.google/bC1TedkCNRgYd3aB6.
            
            Schrijf de e-mail in HTML-formaat zodat deze correct weergegeven wordt in e-mailclients. Zorg voor duidelijke paragrafen, witregels en een professionele uitstraling.
            Sluit af met "Met vriendelijke groeten," zonder extra toevoegingen.
            
            Dit is een voorbeeld van hoe de mail moet worden:
            Hi {first_name},

            {example}

            We hebben jullie website bekeken en denken dat we je bedrijf op de volgende manieren kunnen verbeteren:
            1. Idee 1: korte uitwerking van idee 1 (max 1 zin)
            2. Idee 2: korte uitwerking van idee 2 (max 1 zin)
            3. Idee 3: korte uitwerking van idee 3 (max 1 zin)

            Dit is natuurlijk een gok gebaseerd op wat we op de website zagen. De echte verbeteringen zitten waarschijnlijk verborgen binnen je organisatie.

            Zin in een kort brainstormgesprek van 30 minuten (100% gratis + vrijblijvend!) over hoe AI je bedrijf drastisch kan verbeteren?
            Je kunt hier een tijdslot boeken: Plan een gesprek.
            
              **Credibiliteit:**  
            Optioneel: Vermeld maximaal 2 relevante resultaten of voorbeelden van andere klanten.  
            Bijvoorbeeld:  
            - _Onze klanten zagen een 23% reductie in operationele kosten en een 19% stijging in productiviteit._
            • 32,5% Betere besluitvorming
            • 23,2% Minder operationele kosten
            • 18,6% Hogere productiviteit en kwaliteit
            • 11,6% Minder impact door menselijke fouten
            • 6,9% Meer omzet
            • 6,9% Nauwkeurigere voorspellingen
            
            Ik hoor graag van je! Als je vragen hebt, kun je me altijd een e-mail sturen.

            Met vriendelijke groeten,
            """, sys_message
    else:
        print(category)

        if category == "accomplishment":
            opener = f"Congrats on {first_line}!"
            example = "Congrats on {achieving something}!"

        elif category == "informative":
            opener = f"Saw your post about {first_line}, great insights!"
            example = "Saw your post about {informative topic}, great insights!"

        elif category == "lesson":
            opener = f"Your story about {first_line} on LinkedIn was interesting. Great insights!"
            example = "Your story about {lesson learned} on LinkedIn was interesting. Great insights!"

        elif category == "milestone":
            opener = f"Congrats to you and your team on {first_line}—well done!"
            example = "Congrats to you and your team on {achieved milestone}—well done!"
        else:
            opener = f"I saw you focus on {headline}"
            example = "I saw you focus on {thing}"
        opening_line = "Write an opener based on:  " + opener
        sys_message = (
            "You are a helpful assistant specializing in writing emails for Everyman AI. My name is Luuk Alleman. "
            "Do not use hard or complicated words, we dont want to use much jargon, just keep it super simple and straight forward so anyone can understand it"
            "We sell a service, we dont own products, do not mention anything that sounds like selling something. we just want to look for oppurtunities that could help both sides."
            "Make sure to always align the text to the left as it's an email"
            "The email must be ready to send immediately, so NEVER use placeholders. Write only the salutation and body of the email, and never include the subject line, as we will create that ourselves. "
            "Always write the email in one language, do not mix different languages in one email (except company names etc, but all the other sentences should be the same language)"
            "Write names of companies how you would call them in a face to face conversation, leaving out weird characters, complete (legal) names and just call them in their simple form"
            "End with 'Best regards,' and absolutely never add anything else after that. Be straight to the point and avoid using exaggerated language, Use simple, conversational language and dont use phrases like “enhance transaction security,” “streamline your crypto transactions,” and “predictive analytics” could be flagged because they are commonly used in marketing emails."
            f"""Example of how the email should be written:
                **Greeting:**  
                Hi {first_name},

                **Introduction:**  
                Start with a **specific compliment** or reference to their business. Mention a recent event, product, feature, or service you noticed on their website. in this case it will be about: {opener}

                **Main Body:**  
                - Present **1 to 3 AI solutions** relevant to their business. Be clear, concise, and use everyday language instead of technical jargon.  
                - Describe potential **benefits** (e.g., improving customer service, automating workflows, optimizing internal processes).

                Example:  
                We thought of a few areas where AI could help:  
                1. **Automate customer service:** Integrate AI into your ticketing system to handle support queries quickly and accurately.  
                2. **Streamline internal processes:** Use automation to reduce bottlenecks in core workflows and enhance productivity.  
                3. **Enhance your product:** Add AI features to improve customer experience and boost value.

                **CTA (Call to Action):**  
                Offer a **short consultation** with a friendly tone. Avoid phrases like "100% free." Instead, say:  
                - "Would you be open to a short chat to discuss how AI might support your goals? You can schedule a call here: [Insert link]."

                **Credibility:**  
                You may include **1 to 2 impactful results** from past clients (if relevant). Example:  
                - _"Clients have seen a 23% reduction in operational costs and a 19% increase in productivity."_
                • 32.5% Better decision-making
                • 23.2% Reduction in operational costs
                • 18.6% Increase in productivity and quality
                • 11.6% Fewer impacts from human error
                • 6.9% Revenue growth
                • 6.9% Improved forecasting accuracy 
                
                
                **Closing:**  
                Invite them to reply or ask questions.
                Kind regards,
                """
            "Make sure to add the dynamic content in here, like the ideas that we have come up with. nly return the resulting html, do not add explaination or other text, we need to send this directly to the customer so your response should be the valid html without changing the color of the text"
        )
        if first_line and insights:
            return f"""
            You are an expert in writing professional but very down to earth and easy to understand emails, they should be original and not be too much information. Write a highly personalized cold email to {first_name} with this headline: {headline}.
            
            Start the email with the following fact (this is something they posted on their linkedin, so it's something we're citating from them and want to use as a hook to show we did some research on them) to grab attention, but keep it very short and 1 sentence max! and keep nonchalant by congratiolating them or opening the email in another fun way:: {opening_line}.
            
            list down the nalysis of the company website in a short way to spark their interest and show them we did some research: {insights}.
            
            The goal is to make a connection and offer AI development services through a 30-minute call. 
            This can be scheduled via the following link: https://calendar.app.google/bC1TedkCNRgYd3aB6.
            
             You may include **1 to 2 impactful results** from past clients (if relevant). Example:  
                (choose 2 based on the type of business and the rest of the email)
                • 32.5% Better decision-making
                • 23.2% Reduction in operational costs
                • 18.6% Increase in productivity and quality
                • 11.6% Fewer impacts from human error
                • 6.9% Revenue growth
                • 6.9% Improved forecasting accuracy 
                          
            Write the email in HTML format to ensure proper display in email clients. Use clear paragraphs, white space, and a professional tone.
            Close with "Best regards," without adding anything extra.
            """, sys_message
        elif insights:
            return f"""
            You are an expert in writing professional but very down to earth and easy to understand emails, they should be original and not be too much information. Write a highly personalized cold email to {first_name} with this headline: {headline}.
            
            Open the email with a sharp observation based on this analysis of the company website and then list down the nalysis of the company website in a short way to spark their interest and show them we did some research: {insights}.
          
            The goal is to make a connection and offer AI development services through a 30-minute call. 
            This can be scheduled via the following link: https://calendar.app.google/bC1TedkCNRgYd3aB6.
            
             You may include **1 to 2 impactful results** from past clients (if relevant). Example:  
                (choose 2 based on the type of business and the rest of the email)
                • 32.5% Better decision-making
                • 23.2% Reduction in operational costs
                • 18.6% Increase in productivity and quality
                • 11.6% Fewer impacts from human error
                • 6.9% Revenue growth
                • 6.9% Improved forecasting accuracy  
                         
            Write the email in HTML format to ensure proper display in email clients. Use clear paragraphs, white space, and a professional tone.
            Close with "Best regards," without adding anything extra.
            """, sys_message
        elif first_line:
            return f"""
            You are an expert in writing professional but very down to earth and easy to understand emails, they should be original and not be too much information. Write a highly personalized cold email to {first_name} with this headline: {headline}.
            
            Start the email with the following fact (this is something they posted on their linkedin, so it's something we're citating from them and want to use as a hook to show we did some research on them) to grab attention, but keep it very short and 1 sentence max! and keep nonchalant by congratiolating them or opening the email in another fun way:: {opening_line}.
            
            The goal is to make a connection and offer AI development services (keep those basic, just like the example that you are provided) through a 30-minute call. 
            This can be scheduled via the following link: https://calendar.app.google/bC1TedkCNRgYd3aB6.
             You may include **1 to 2 impactful results** from past clients (if relevant). Example:  
                (choose 2 based on the type of business and the rest of the email)
                • 32.5% Better decision-making
                • 23.2% Reduction in operational costs
                • 18.6% Increase in productivity and quality
                • 11.6% Fewer impacts from human error
                • 6.9% Revenue growth
                • 6.9% Improved forecasting accuracy
                
            Write the email in HTML format to ensure proper display in email clients. Use clear paragraphs, white space, and a professional tone.
            Close with "Best regards," without adding anything extra.
            """, sys_message
        else:
            return f"""
            You are an expert in writing professional but very down to earth and easy to understand emails, they should be original and not be too much information. Write a highly personalized cold email to {first_name} with this headline: {headline}.
                        
            The goal is to make a connection and offer AI development services through a 30-minute call. 
            This can be scheduled via the following link: https://calendar.app.google/bC1TedkCNRgYd3aB6.
            
            Write it out based on this information we have on this person: {headline}
            Write the email in HTML format to ensure proper display in email clients. Use clear paragraphs, white space, and a professional tone.
            Close with "Best regards," without adding anything extra.
            This is how the email should look like:
                Hi {first_name},

                {example}

                We checked your website and think we could improve your business in the following ways:
                1. Idea 1: short explanation of idea 1 (max 1 sentence)
                2. Idea 2: short explanation of idea 2 (max 1 sentence)
                3. Idea 3: short explanation of idea 3 (max 1 sentence)

                This is, of course, a guess based on what we saw on your website. The real improvements are likely hidden inside your organization.

                Interested in a short 30-minute brainstorm (100% free and no strings attached!) about how AI could drastically improve your business?
                You can book a time slot here: Schedule a call.

             You may include **1 to 2 impactful results** from past clients (if relevant). Example:  
                (choose 2 based on the type of business and the rest of the email)
                • 32.5% Better decision-making
                • 23.2% Reduction in operational costs
                • 18.6% Increase in productivity and quality
                • 11.6% Fewer impacts from human error
                • 6.9% Revenue growth
                • 6.9% Improved forecasting accuracy

                I’d love to hear from you! If you have any questions, feel free to email me.

                Kind regards,
            """, sys_message


def get_website_analysis_prompt(content, language):
    if language == "NL":
        analysis_prompt = f"""
                Je bent een zeer geavanceerd en professioneel AI-model dat gespecialiseerd is in het analyseren van bedrijfsactiviteiten 
                en het voorstellen van AI-oplossingen die aansluiten bij de expertise van Everyman AI. Everyman AI biedt op maat gemaakte oplossingen 
                die bedrijven helpen hun processen te optimaliseren, klantinteracties te verbeteren en datagedreven beslissingen te nemen. 
                Daarnaast kunnen we ook volledig interne processen optimaliseren door AI-implementaties.

                Voorbeelden van oplossingen die we kunnen bouwen (maar niet beperkt tot):
                - AI-agents voor het automatiseren van e-mailbeheer, documentanalyse en gepersonaliseerde klantcommunicatie.
                - Machine learning-modellen voor voorspellingen, klantsegmentatie en aanbevelingssystemen.
                - Tools voor procesautomatisering, zoals voorraadbeheer, planningsoptimalisatie en workflowverbeteringen.
                - AI-oplossingen voor marketingpersonalisatie en trendanalyse gebaseerd op klantgedrag.
                - Sentimentanalyse en inzichten uit klantfeedback en sociale media.

                Analyseer zorgvuldig de volgende inhoud van de bedrijfswebsite:
                {content}

                Je taak is om:
                De informatie over dit bedrijf te bekijken en drie mogelijke projecten voor te stellen die we hen kunnen aanbieden, zodat ze een idee krijgen van wat AI voor hen kan betekenen. De ideeën moeten echt waardevol zijn voor hun specifieke bedrijfsactiviteiten. Schrijf deze drie ideeen kort en bondig uit.

                Als het bedrijf een bureau is, kunnen we ook voorstellen om samen te werken als partners.
                Zorg ervoor dat je aanbevelingen direct toepasbaar zijn en aansluiten bij de beschreven activiteiten van het bedrijf.
                Schrijf op een professionele, informatieve en overtuigende manier.
                """
        sys_message = "Je bent een behulpzame AI gespecialiseerd in bedrijfsanalyses en AI-oplossingen. Je krijgt de content van een website van een mogelijke klant."

    else:
        analysis_prompt = f"""
                You are a highly advanced and professional AI model specialized in analyzing business activities 
                and proposing AI solutions that align with the expertise of Everyman AI. Everyman AI provides tailored 
                solutions that help businesses optimize their processes, improve customer interactions, and make data-driven decisions, but we can also completely optimize their internal processes by implementing AI.

                Examples things be can build (but not limited to):
                - AI agents for automating email management, document analysis, and personalized customer communication.
                - Machine learning models for predictions, customer segmentation, and recommendation systems.
                - Tools for process automation, such as inventory management, scheduling optimization, and workflow improvements.
                - AI solutions for marketing personalization and trend analysis based on customer behavior.
                - Sentiment analysis and insights from customer feedback and social media.

                Carefully analyze the following company website content:
                {content}

                Your task is to:
                Look at the information of this business, and come three up with some possible projects we could offer them to give them an idea of what AI could do for them. The 3 ideas should be really valuable for their specific business. Write the 3 ideas out shortly
                
                If the company is an agency, we could also suggest partnering up together.
                Ensure your recommendations are directly applicable and align with the described activities of the company. 
                Write in a professional, informative, and persuasive style.
                """
        sys_message = "You are a helpful AI assistant that helps analyse a website and finds any services we could offer as an AI agency to them"
    return analysis_prompt, sys_message


def get_analysis_prompt(posts, language):
    """
    Returns a language-specific analysis prompt based on LinkedIn posts.
    """
    if language.lower() == "nl":
        prompt = f"""
        Je bent een geavanceerde AI gespecialiseerd in het analyseren van LinkedIn-berichten. Hier is een lijst met recente LinkedIn-berichten van een persoon:

        LinkedIn berichten:
        {posts}

        Haal uit de berichten één specifieke gebeurtenis, detail of prestatie die het meeest relevant, opvallend en boeiend is om te gebruiken als cold email opening line. 
        Dit mag alleen worden geleverd als het iets is wat echt relevant is en een positieve indruk kan maken—geen algemene uitspraken of irrelevante details, 
        gebruik aankondigingen, behaalde doelen of dingen die echt persoonlijk zijn.
        
        Lever het resultaat als één enkele zin aan die gebruikt kan worden als opener in een email naar deze persoon, zonder aanhef als geachte ..., afsluiting of extra context. 
        De zin moet direct overgenomen kunnen worden als input voor een verdere e-mailgeneratie.
        
        Gebruik geen algemene uitspraken, maar focus op concret persoonlijke details. 
        Als dit bruikbaar is als opener van een cold email, dan moet useable True zijn, anders False.
        kies tussen de volgende categorien: accomplishment, informative, lesson, milestone
        """
        sys_message = """Je bent een assistent die LinkedIn-berichten analyseert om een openingszin voor een cold email te extraheren. 
        Schrijf het alsof we dit bericht lezen en een gesprek met de persoon willen beginnen. 
        Het moet een zeer korte oneliner zijn zonder te veel details. Schrijf het natuurlijk, alsof je een e-mail begint. 

        Schrijf bedrijfsnamen normaal uit, zonder onnodige hoofdletters, speciale symbolen of opmaak. 
        Het moet aanvoelen als een zin die ik zou schrijven om een e-mail aan iemand te openen.

        Bepaal of het bericht geschikt is als opener voor een cold email. Wees hierbij heel selectief—het moet iets belangrijks of noemenswaardigs zijn. 
        Hieronder staan voorbeelden van wat *wel* en *niet* geschikt is voor een cold email opener:

        ---

        ### **Voorbeelden van geschikte inhoud voor een cold email opener:**
        1. **Aankondiging van promotie:**  
        "Gefeliciteerd met je recente promotie tot Hoofd Verkoop!"

        2. **Lancering van een product:**  
        "Ik zag je bericht over de nieuwe AI-tool die je bedrijf heeft gelanceerd—spannend!"

        3. **Informatieve content:**  
        "Ik las je inzichten over marketingtrends—echt inspirerend."

        4. **Zakelijke mijlpaal:**  
        "Gefeliciteerd met het behalen van jullie omzetdoel!"

        5. **Erkenning of prijs:**  
        "Ik zag dat je werd erkend als een van de topinnovators in je branche—dik verdiend!"

        ---

        ### **Voorbeelden van ongeschikte inhoud voor een cold email opener:**
        1. **Bericht over een baanzoektocht:**  
        Voorbeeld: "Mijn vriend John zoekt een baan in marketing—kan iemand helpen?"
        - Niet relevant voor de ontvanger in een zakelijke context.

        2. **Persoonlijke statusupdate:**  
        Voorbeeld: "Dankbaar voor dit lange weekend met familie."
        - Te persoonlijk en irrelevant voor een zakelijke email-opener.

        3. **Memes of informele grappen:**  
        Voorbeeld: "Maandagblues—gelukkig is er koffie!"
        - Mist relevantie of belang voor een zakelijke conversatie.

        4. **Interne teamcomplimenten:**  
        Voorbeeld: "Complimenten aan mijn collega Jane voor het organiseren van ons teamuitje!"
        - Interne erkenning is niet impactvol voor een externe conversatie.

        5. **Algemeen felicitatiebericht:**  
        Voorbeeld: "Gefeliciteerd aan de klas van 2025 met afstuderen!"
        - Generieke aankondigingen zijn niet interessant genoeg.

        ---

        Zorg ervoor dat je reactie overeenkomt met deze criteria en voorbeelden."""
        return prompt, sys_message
    else:
        prompt = f"""
        You are an advanced AI specialized in analyzing LinkedIn posts. Here is a list of recent LinkedIn posts from a person:

        LinkedIn posts:
        {posts}

        Extract one specific event, detail, or achievement from the posts that is relevant, noteworthy, and engaging to use as a cold email opening line. 
        Provide this only if it is something genuinely relevant that leaves a positive impression—no general statements or irrelevant details, 
        only things like impressive achievements, announcements, or something they say about themselves.

        Deliver the result as a single sentence, without a salutation (like Dear ...), closing, or extra context. 
        The sentence must be directly usable as input for further email generation.

        Avoid general statements and focus on concrete details. 
        If this can be used as an opener for a cold email, set `useable` to True; otherwise, set it to False.
        choose between the following categories: accomplishment, informative, lesson, milestone
        """
        sys_message = """You are an assistant analyzing LinkedIn posts to extract a cold email opener. 
            Write in the form as if we read this and want to start a conversation with the person. 
            This should be a very short oneliner without too much detail. Write it naturally, as if starting an email. 

            Also, write out company names normally, without adding unnecessary capital letters, special symbols, or formatting.
            It should feel like a line I would write if I wanted to open an email to someone.

            Determine if the post is suitable for a cold email opener. Be very selective—we only want to open an email with something significant or worth mentioning.
            Below are examples of what *can* and *cannot* be used as a cold email opener:

            ---

            ### **Examples of suitable content for a cold email opener:**
            1. **Promotion announcement:**  
            "Congrats on your recent promotion to Head of Sales!"

            2. **Product launch:**  
            "Saw your post about the new AI tool your company launched—exciting stuff!"

            3. **Informative content:**  
            "I read your insights about marketing trends—really thought-provoking."

            4. **Business milestone:**  
            "Congrats to you and your team for hitting your revenue goal!"

            5. **Recognition or award:**  
            "Saw you were recognized as one of the top innovators in your industry—well-deserved!"

            ---

            ### **Examples of unsuitable content for a cold email opener:**
            1. **Job search post:**  
            Example: "My friend John is looking for a job in marketing—can anyone help?"
            - Not business-relevant to the recipient.

            2. **Personal status update:**  
            Example: "Feeling grateful for this long weekend with family."
            - Too personal and irrelevant for a professional email opener.

            3. **Memes or casual jokes:**  
            Example: "The Monday blues hit hard—thank God for coffee!"
            - Lacks significance or relevance for a business conversation.

            4. **Internal team shoutouts:**  
            Example: "Kudos to my colleague Jane for organizing our team-building event!"
            - Internal recognition is not impactful for an external conversation.

            5. **Random congratulatory post:**  
            Example: "Congrats to the class of 2025 on graduating!"
            - Generic announcements are not engaging enough.

            ---

            Ensure that your response aligns with these criteria and examples."""
        return prompt, sys_message


def get_language_prompt(posts, name):
    """
    Returns the language detection prompt for analyzing LinkedIn posts.
    """
    return f"""
    You are an advanced AI specialized in analyzing LinkedIn posts for language and also analysing their name. Here is a list of recent LinkedIn posts from a person:

    LinkedIn posts:
    {posts}

    Name: {name}
    
    Specify the language spoken (language_spoken) by this person and analyse their name. Choose either EN (English) if ONLY English is used in the linkedin posts and if their name is not dutch(indicating that this is the only language this person knows), 
    or NL (Dutch) if Dutch is found anywhere in the linkedin posts or if their name is clearly dutch (if the person has written a post in Dutch, this indicates Dutch as their primary language).
    """
