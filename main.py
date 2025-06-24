import discord
from discord.ext import commands, tasks
import os
import random
import time
import asyncio

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='.', intents=intents)

# Önbellek değişkenleri
cache_servisler = []
cache_toplam = 0

def hesap_sayisi_ve_servisler():
    toplam = 0
    servisler = []

    for dosya in os.listdir():
        if dosya.endswith(".txt"):
            with open(dosya, "r", encoding="utf-8") as f:
                satir_sayisi = sum(1 for line in f if ":" in line)
                toplam += satir_sayisi
                isim = dosya[:-4].capitalize()
                servisler.append(f"✅ {isim} ({satir_sayisi} hesap)")
    return toplam, servisler


async def presence_guncelle_loop():
    await bot.wait_until_ready()
    while not bot.is_closed():
        toplam = hesap_sayisi()
        await bot.change_presence(activity=discord.Game(name=f"Total Acc: {toplam}"))
        await asyncio.sleep(60)

@bot.event
async def on_ready():
    bot.loop.create_task(presence_guncelle_loop())
    print(f'{bot.user} olarak giriş yapıldı.')
    global cache_toplam, cache_servisler
    cache_toplam, cache_servisler = hesap_sayisi_ve_servisler()
    cache_guncelle.start()

@tasks.loop(minutes=5)
async def cache_guncelle():
    global cache_toplam, cache_servisler
    cache_toplam, cache_servisler = hesap_sayisi_ve_servisler()
    print("Önbellek güncellendi.")

def hesap_sayisi():
    # Gen komutu için anlık toplam hesap sayısı
    toplam = 0
    for dosya in os.listdir():
        if dosya.endswith(".txt"):
            with open(dosya, "r", encoding="utf-8") as f:
                toplam += sum(1 for line in f if ":" in line)
    return toplam

@bot.event
async def on_message(message):
    # Komutları kullanabilmek için on_message override edildiğinde bot.process_commands çağrılmalı
    if message.author == bot.user:
        return
    await bot.process_commands(message)

@bot.command()
async def ping(ctx):
    ping_ms = round(bot.latency * 1000)
    await ctx.send(f"Pong! {ping_ms}ms")

last_gen_usage = {}

@bot.command()
async def gen(ctx, servis: str):
    cooldown = 30
    user_id = ctx.author.id
    now = time.time()

    if user_id in last_gen_usage:
        elapsed = now - last_gen_usage[user_id]
        if elapsed < cooldown:
            kalan = int(cooldown - elapsed)
            await ctx.send(f"Lütfen {kalan} saniye bekleyin.")
            return

    dosya_adi = f"{servis.lower()}.txt"

    if not os.path.exists(dosya_adi):
        await ctx.send(f"❌ `{servis}` adlı bir servis bulunamadı.")
        return

    with open(dosya_adi, "r", encoding="utf-8") as f:
        satirlar = [satir.strip() for satir in f if ":" in satir]

    if not satirlar:
        await ctx.send(f"⚠️ `{servis}` servisi için kayıtlı hesap yok.")
        return

    secilen = random.choice(satirlar)
    kullanici, sifre = secilen.split(":", 1)

    embed = discord.Embed(
        title="🔐 Hesap Üretildi!",
        description=f"**Hizmet:** `{servis}`\n\n**👤 Hesap Adı:** `{kullanici.strip()}`\n**🔑 Şifre:** `{sifre.strip()}`",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

    last_gen_usage[user_id] = now

@bot.command()
async def info(ctx):
    global cache_toplam, cache_servisler

    description = (
        "Bu bot çeşitli servisler için hesap üretir. Kullanabileceğin komutlar:\n\n"
        "`.gen <servis>` → Belirtilen servis için rastgele hesap üretir.\n"
        "`.info` → Bu mesajı gösterir.\n\n"
        f"**📦 Kullanılabilir Servisler:**\n" + "\n".join(cache_servisler) +
        f"\n\n**🧮 Total Acc:** `{cache_toplam}`"
    )

    embed = discord.Embed(
        title="📜 Bot Bilgisi",
        description=description,
        color=discord.Color.blue()
    )
    embed.set_footer(text="👾 Powered by WolfHack")
    await ctx.send(embed=embed)

bot.run(TOKEN)
