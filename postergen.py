from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import os
import pandas as pd
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont
import io

# Configure the Generative AI with the provided API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def get_gemini_response(input_prompt, images, prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input_prompt] + images + [prompt])
    return response.text

def input_image_setup(uploaded_files):
    image_parts = []
    for uploaded_file in uploaded_files:
        if uploaded_file is not None:
            bytes_data = uploaded_file.getvalue()
            image_parts.append({
                "mime_type": uploaded_file.type,
                "data": bytes_data
            })
        else:
            raise FileNotFoundError("No file uploaded")
    return image_parts

def place_elements(template, logo, product_images, logo_size, logo_position, product_size, product_position, headline, headline_position, subheadline, subheadline_position, cta_button, cta_button_position, contact_details, contact_details_position, website_details, website_details_position):
    template_image = Image.open(template).convert("RGBA")
    draw = ImageDraw.Draw(template_image)
    font_headline = ImageFont.truetype("arial.ttf", 36)  # Font size for headline
    font_subheadline = ImageFont.truetype("arial.ttf", 24)  # Font size for subheadline
    font_description = ImageFont.truetype("arial.ttf", 18)  # Font size for description

    logo_image = Image.open(io.BytesIO(logo['data'])).convert("RGBA")
    logo_image = logo_image.resize(logo_size)
    template_image.paste(logo_image, logo_position, logo_image)

    for product_image in product_images:
        image = Image.open(io.BytesIO(product_image['data'])).convert("RGBA")
        image = image.resize(product_size)
        template_image.paste(image, product_position, image)

    # Draw text elements
    draw.text(headline_position, headline, font=font_headline, fill="black")
    draw.text(subheadline_position, subheadline, font=font_subheadline, fill="black")
    draw.text(cta_button_position, cta_button, font=font_description, fill="black")
    draw.text(contact_details_position, contact_details, font=font_description, fill="black")
    draw.text(website_details_position, website_details, font=font_description, fill="black")

    return template_image

st.set_page_config(page_title="Social Media Post Creator")

st.header("Social Media Post Creator")
st.subheader("Generate professional social media posts with your brand identity")

st.markdown("### Brand Identity")
brand_name = st.text_input("Enter your brand name:")
brand_description = st.text_area("Enter a description for your brand:")
brand_logo = st.file_uploader("Upload your brand logo (JPG, PNG):", type=["jpg", "jpeg", "png"])

st.markdown("#### Choose brand colors:")
primary_color = st.color_picker("Primary color:")
secondary_color = st.color_picker("Secondary color:")
tertiary_color = st.color_picker("Tertiary color:")

st.markdown("### Product Listing")
uploaded_files = st.file_uploader("Upload product images (JPG, PNG):", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
add_more = st.button("Add More")

if uploaded_files:
    for uploaded_file in uploaded_files:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Product Image.", use_column_width=True)

st.markdown("### Company Details")
email_id = st.text_input("Enter your email ID:")
contact_number = st.text_input("Enter your contact number:")
website = st.text_input("Enter your website:")

input_prompt = st.text_input("Enter a description for your social media post:", key="input")

st.markdown("### Template Selection")
template_folder = 'temp'
template_files = ['template1.jpg', 'template2.jpg', 'template3.jpg']
templates = [os.path.join(template_folder, template_file) for template_file in template_files]

template_options = {}
for i, template_path in enumerate(templates):
    template_options[f"Template {i+1}"] = template_path

template_selection = st.selectbox("Choose a template for your post:", list(template_options.keys()))

submit = st.button("Generate Post")

input_prompt_text = """
System: Welcome to the Social Media Post Creator. This system helps generate social media posts using AI. 
Use the provided templates to create engaging posts tailored to your brand identity. Describe the desired content of the post, and the system will 
identify the product image and generate a catchy 
        1. Headline (max 4 words), 
        2. Sub-headline (max 10 words),
        3. Product description (max 25 words). 
        The generated content, along with the logo and product images, will be integrated into the selected template.
"""

if submit:
    if uploaded_files and brand_logo and (primary_color or secondary_color or tertiary_color):
        try:
            image_data = input_image_setup(uploaded_files)
            logo_data = input_image_setup([brand_logo])[0]
            image_data.insert(0, logo_data)
            response = get_gemini_response(input_prompt_text, image_data, input_prompt)
            st.subheader("Generated Post")
            st.write(response)

            # Extract generated headline, subheadline, and description from the response
            lines = response.splitlines()
            if len(lines) >= 3:
                headline = lines[0]  # First line as headline
                subheadline = lines[1]  # Second line as subheadline
                description = lines[2]  # Third line as description

                # Append company details to the description
                contact_details = f"Contact: {contact_number}\nEmail: {email_id}"
                website_details = f"Website: {website}"

                # Fixed positions
                logo_size = (100, 100)
                logo_position = (30, 30)
                headline_position = (30, 100)
                subheadline_position = (30, 160)
                product_size = (300, 300)
                product_position = (400, 100)
                cta_button = "Buy Now"  # Example CTA button text
                cta_button_position = (300, 550)
                contact_details_position = (30, 700)
                website_details_position = (300, 700)

                selected_template = template_options[template_selection]
                final_poster = place_elements(
                    selected_template,
                    logo_data,
                    image_data[1:],
                    logo_size,
                    logo_position,
                    product_size,
                    product_position,
                    headline,
                    headline_position,
                    subheadline,
                    subheadline_position,
                    cta_button,
                    cta_button_position,
                    contact_details,
                    contact_details_position,
                    website_details,
                    website_details_position
                )

                st.image(final_poster, caption="Final Poster", use_column_width=True)

                download_buffer = io.BytesIO()
                final_poster.convert("RGB").save(download_buffer, format="JPEG")
                download_buffer.seek(0)
                st.download_button(
                    label="Download Final Poster",
                    data=download_buffer,
                    file_name="final_poster.jpg",
                    mime="image/jpeg"
                )
            else:
                st.error("Failed to extract headline, subheadline, and description from the response.")
        except ValueError as e:
            st.error(f"Error: {e}")
    else:
        st.error("Please upload a brand logo, select at least one color, and upload at least one product image.")

if brand_logo:
    logo_image = Image.open(brand_logo)
    st.image(logo_image, caption="Brand Logo", use_column_width=True)

if primary_color:
    st.markdown(f"**Primary Color:** {primary_color}")
if secondary_color:
    st.markdown(f"**Secondary Color:** {secondary_color}")
if tertiary_color:
    st.markdown(f"**Tertiary Color:** {tertiary_color}")

# Preview Section
st.markdown("### Preview Section")
if uploaded_files and brand_logo:
    image_data = input_image_setup(uploaded_files)
    logo_data = input_image_setup([brand_logo])[0]
    preview_template = template_options[template_selection]
    preview_poster = place_elements(
        preview_template,
        logo_data,
        image_data,
        (100, 100),
        (30, 30),
        (300, 300),
        (400, 100),
        "Headline",
        (30, 100),
        "Subheadline",
        (30, 160),
        "Buy Now",
        (300, 550),
        "Contact: 1234567890\nEmail: example@example.com",
        (30, 700),
        "Website: www.example.com",
        (300, 700)
    )
    st.image(preview_poster, caption="Preview Poster", use_column_width=True)
