import { useEffect, useMemo, useState } from "react";
import {
  ArrowLeft, Search, ShoppingBag, Home, LayoutGrid, UserRound,
  Plus, Minus, Trash2, ChevronRight, Sparkles, ShieldCheck,
  Zap, Tag, X, Crown
} from "lucide-react";
import { createOrder, getGames, getSubscriptions, getSettings } from "./api";

const tg = window.Telegram?.WebApp;
const demoUser = { id: "demo_telegram_user", first_name: "Гость", username: "" };

function money(value) {
  return new Intl.NumberFormat("ru-RU").format(Math.round(value)) + " ₽";
}

function App() {
  const [page, setPage] = useState("home");
  const [games, setGames] = useState([]);
  const [settings, setSettings] = useState({try_rub: 2.28, markup: 0.10});
  const [subscriptions, setSubscriptions] = useState([]);
  const [cart, setCart] = useState(() => JSON.parse(localStorage.getItem("cart") || "[]"));
  const [selectedGame, setSelectedGame] = useState(null);
  const [search, setSearch] = useState("");
  const [platform, setPlatform] = useState("all");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    tg?.ready();
    tg?.expand();
    if (tg?.setHeaderColor) tg.setHeaderColor("#070A12");
    if (tg?.setBackgroundColor) tg.setBackgroundColor("#070A12");
  }, []);

  useEffect(() => {
    Promise.all([getGames(), getSubscriptions(), getSettings()])
      .then(([g, plus, s]) => { setGames(g); setSubscriptions(plus); setSettings(s); })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    localStorage.setItem("cart", JSON.stringify(cart));
  }, [cart]);

  const cartCount = cart.reduce((sum, item) => sum + item.quantity, 0);
  const cartTotal = cart.reduce((sum, item) => sum + item.price_rub * item.quantity, 0);
  const featured = games.filter(g => g.featured);
  const filtered = games.filter(g => {
    const matchText = g.title.toLowerCase().includes(search.toLowerCase());
    const matchPlatform = platform === "all" || g.platform.includes(platform);
    return matchText && matchPlatform;
  });

  function addToCart(item) {
    const cartKey = `${item.type || "game"}-${item.id}`;
    setCart(prev => {
      const found = prev.find(x => (x.cartKey || `${x.type || "game"}-${x.id}`) === cartKey);
      if (found) return prev.map(x => (x.cartKey || `${x.type || "game"}-${x.id}`) === cartKey ? {...x, cartKey, quantity: x.quantity + 1} : x);
      return [...prev, {...item, cartKey, quantity: 1}];
    });
  }

  function updateQty(cartKey, delta) {
    setCart(prev => prev
      .map(x => (x.cartKey || `${x.type || "game"}-${x.id}`) === cartKey ? {...x, cartKey, quantity: x.quantity + delta} : x)
      .filter(x => x.quantity > 0)
    );
  }

  function openGame(game) {
    setSelectedGame(game);
    setPage("game");
    window.scrollTo({top: 0, behavior: "smooth"});
  }

  function nav(next) {
    setPage(next);
    setSelectedGame(null);
    window.scrollTo({top: 0, behavior: "smooth"});
  }

  return (
    <div className="app">
      <div className="ambient ambient-one" />
      <div className="ambient ambient-two" />
      {page === "home" && (
        <HomePage
          featured={featured}
          games={games}
          onOpen={openGame}
          onCatalog={() => nav("catalog")}
          onPlus={() => nav("plus")}
          onCart={() => nav("cart")}
          cartCount={cartCount}
          user={tg?.initDataUnsafe?.user || demoUser}
        />
      )}
      {page === "catalog" && (
        <CatalogPage
          games={filtered}
          search={search}
          setSearch={setSearch}
          platform={platform}
          setPlatform={setPlatform}
          onOpen={openGame}
          onAdd={addToCart}
          loading={loading}
        />
      )}
      {page === "plus" && (
        <PlusPage
          subscriptions={subscriptions}
          onAdd={addToCart}
          onCart={() => nav("cart")}
          cartCount={cartCount}
        />
      )}
      {page === "game" && selectedGame && (
        <GamePage
          game={selectedGame}
          onBack={() => nav("catalog")}
          onAdd={() => addToCart(selectedGame)}
        />
      )}
      {page === "cart" && (
        <CartPage
          cart={cart}
          total={cartTotal}
          onQty={updateQty}
          onBack={() => nav("home")}
          onCheckout={() => nav("checkout")}
          onOpen={openGame}
        />
      )}
      {page === "checkout" && (
        <CheckoutPage
          cart={cart}
          total={cartTotal}
          onBack={() => nav("cart")}
          onClear={() => setCart([])}
        />
      )}
      {page === "profile" && (
        <ProfilePage user={tg?.initDataUnsafe?.user || demoUser} onOrders={() => {}} />
      )}

      {!["game", "checkout"].includes(page) && (
        <BottomNav page={page} setPage={nav} cartCount={cartCount} />
      )}
    </div>
  );
}

function Header({title, back, onBack, cartCount, onCart}) {
  return (
    <header className="topbar">
      <div className="brand">
        {back ? <button className="icon-btn" onClick={onBack}><ArrowLeft size={20}/></button> : <div className="brand-mark">✦</div>}
        <div><div className="brand-name">{title || "24XSTORE"}</div><div className="brand-sub">Игры для PlayStation</div></div>
      </div>
      {!back && <button className="cart-head" onClick={onCart}><ShoppingBag size={19}/><span>{cartCount}</span></button>}
    </header>
  );
}

function HomePage({featured, games, onOpen, onCatalog, onPlus, onCart, cartCount, user}) {
  const hero = featured[0] || games[0];
  return (
    <>
      <Header cartCount={cartCount} onCart={onCart}/>
      <main className="content">
        <section className="welcome">
          <div>
            <span className="eyebrow">ДЛЯ ТЕБЯ</span>
            <h1>Игры, которые<br/><span>хочется пройти.</span></h1>
            <p>Актуальные предложения PlayStation в одном месте.</p>
          </div>
          <div className="avatar">{(user.first_name || "G").slice(0,1).toUpperCase()}</div>
        </section>

        {hero && <section className="hero" onClick={() => onOpen(hero)}>
          <img src={hero.image} alt="" />
          <div className="hero-shade"/>
          <div className="hero-info">
            <span className="pill blue">PS5</span>
            <h2>{hero.title}</h2>
            <p>Премиальное предложение</p>
            <strong>{money(hero.price_rub)}</strong>
          </div>
          <ChevronRight className="hero-arrow"/>
        </section>}

        <section className="quick-grid">
          <Quick icon={<Sparkles/>} title="Новинки" onClick={onCatalog}/>
          <Quick icon={<ShieldCheck/>} title="PS5" onClick={onCatalog}/>
          <Quick icon={<Zap/>} title="PS4" onClick={onCatalog}/>
          <Quick icon={<Crown/>} title="PS Plus" onClick={onPlus}/>
        </section>

        <SectionTitle title="Популярное" action="Весь каталог" onClick={onCatalog}/>
        <div className="horizontal-games">
          {featured.slice(0,4).map(game => <GameCard key={game.id} game={game} onOpen={onOpen}/>)}
        </div>

        <SectionTitle title="Выгодные покупки" action="Смотреть всё" onClick={onCatalog}/>
        <div className="compact-list">
          {games.slice(0,3).map(game => <CompactGame key={game.id} game={game} onOpen={onOpen}/>)}
        </div>

        <div className="trust-card">
          <div className="trust-icon"><ShieldCheck/></div>
          <div><b>Честная цена</b><p>Курс TRY/RUB и наценка рассчитываются автоматически.</p></div>
        </div>
      </main>
    </>
  );
}

function Quick({icon,title,onClick}) {
  return <button className="quick" onClick={onClick}><span>{icon}</span><b>{title}</b></button>;
}

function SectionTitle({title, action, onClick}) {
  return <div className="section-title"><h3>{title}</h3><button onClick={onClick}>{action}<ChevronRight size={15}/></button></div>;
}

function GameCard({game,onOpen}) {
  return <button className="game-card" onClick={() => onOpen(game)}>
    <div className="cover"><img src={game.image} alt=""/><span className="platform-badge">{game.platform.split(" / ")[0]}</span>{game.discount_percent>0&&<span className="discount-badge">-{game.discount_percent}%</span>}</div>
    <div className="game-title">{game.title}</div>
    <div className="game-price">{money(game.price_rub)}</div>
  </button>;
}

function CompactGame({game,onOpen}) {
  return <button className="compact-game" onClick={() => onOpen(game)}>
    <img src={game.image} alt=""/>
    <div className="compact-info"><b>{game.title}</b><span>{game.platform}</span><strong>{money(game.price_rub)}</strong></div>
    <ChevronRight size={18}/>
  </button>;
}

function CatalogPage({games,search,setSearch,platform,setPlatform,onOpen,onAdd,loading}) {
  return <>
    <Header title="Каталог" back onBack={() => window.history.back()}/>
    <main className="content">
      <div className="search"><Search size={18}/><input value={search} onChange={e=>setSearch(e.target.value)} placeholder="Найти игру..."/>{search && <button onClick={()=>setSearch("")}><X size={16}/></button>}</div>
      <div className="filters">
        {["all","PS5","PS4"].map(x=><button className={platform===x?"active":""} onClick={()=>setPlatform(x)} key={x}>{x==="all"?"Все":x}</button>)}
      </div>
      <div className="catalog-meta"><span>{games.length} игр</span><span>По популярности ↓</span></div>
      {loading ? <div className="loading">Загрузка каталога...</div> : <div className="catalog-list">
        {games.map(game => <div className="catalog-item" key={game.id}>
          <button className="catalog-main" onClick={()=>onOpen(game)}><img src={game.image} alt=""/><div><b>{game.title}</b><span>{game.platform}</span><strong>{money(game.price_rub)}</strong></div></button>
          <button className="add-btn" onClick={()=>onAdd(game)}><ShoppingBag size={18}/></button>
        </div>)}
      </div>}
    </main>
  </>;
}

function GamePage({game,onBack,onAdd}) {
  return <>
    <Header title="Игра" back onBack={onBack}/>
    <main className="content game-page">
      <div className="detail-cover"><img src={game.image} alt=""/><div className="detail-overlay"/></div>
      <div className="detail-content">
        <div className="detail-pills"><span className="pill blue">{game.platform}</span><span className="pill">Турция</span></div>
        <h1>{game.title}</h1>
        <div className="rating"><b>PlayStation Store Turkey</b></div>
        <div className="price-box"><div><span>Цена в магазине</span><strong>{money(game.price_rub)}</strong></div><em>+10%</em><p>Рассчитано по текущему курсу TRY/RUB</p></div>
        <h3>Описание</h3><p className="description">{game.description}</p>
        <button className="primary wide" onClick={onAdd}><ShoppingBag size={19}/> Добавить в корзину</button>
      </div>
    </main>
  </>;
}

function PlusPage({subscriptions,onAdd,onCart,cartCount}) {
  const tiers=["Essential","Extra","Deluxe"];
  return <>
    <Header title="PS Plus" cartCount={cartCount} onCart={onCart}/>
    <main className="content">
      <section className="plus-hero">
        <div className="plus-logo"><Crown/></div>
        <div><span className="eyebrow">PLAYSTATION PLUS</span><h1>Больше игр.<br/><span>Больше возможностей.</span></h1><p>Подписки для турецкого региона. Цена автоматически пересчитывается в рубли.</p></div>
      </section>
      {tiers.map(tier=>{
        const items=subscriptions.filter(x=>x.tier===tier);
        if(!items.length)return null;
        return <section className="plus-tier" key={tier}>
          <SectionTitle title={tier} action={`${items.length} варианта`}/>
          <div className="plus-list">
            {items.map(item=><div className="plus-card" key={item.id}>
              <div className={`tier-icon ${tier.toLowerCase()}`}><Crown/></div>
              <div className="plus-info"><b>{item.title}</b><span>{item.duration_months} мес. · Турция</span><strong>{item.price_rub == null ? "Цена уточняется" : money(item.price_rub)}</strong></div>
              <button className="add-btn" disabled={item.price_rub == null} onClick={()=>onAdd(item)}><ShoppingBag size={18}/></button>
            </div>)}
          </div>
        </section>;
      })}
      <div className="trust-card"><div className="trust-icon"><ShieldCheck/></div><div><b>Три уровня PS Plus</b><p>Essential, Extra и Deluxe. Перед продажей проверяем актуальную цену турецкого региона.</p></div></div>
    </main>
  </>;
}

function CartPage({cart,total,onQty,onBack,onCheckout,onOpen}) {
  return <>
    <Header title="Корзина" back onBack={onBack}/>
    <main className="content">
      {cart.length===0 ? <EmptyCart/> : <>
        <div className="cart-items">{cart.map(item=><div className="cart-item" key={item.cartKey || `${item.type || "game"}-${item.id}`}>
          <img src={item.image} alt="" onClick={()=>item.type!=="subscription"&&onOpen(item)}/>
          <div className="cart-item-info"><b>{item.title}</b><span>{item.platform || `PS Plus ${item.tier}`}</span><strong>{money(item.price_rub)}</strong><div className="qty"><button onClick={()=>onQty(item.cartKey || `${item.type || "game"}-${item.id}`,-1)}><Minus size={14}/></button><b>{item.quantity}</b><button onClick={()=>onQty(item.cartKey || `${item.type || "game"}-${item.id}`,1)}><Plus size={14}/></button></div></div>
          <button className="delete" onClick={()=>onQty(item.cartKey || `${item.type || "game"}-${item.id}`,-item.quantity)}><Trash2 size={16}/></button>
        </div>)}</div>
        <div className="summary"><div><span>Товаров</span><b>{cart.reduce((s,x)=>s+x.quantity,0)}</b></div><div className="total"><span>Итого</span><strong>{money(total)}</strong></div></div>
        <button className="primary wide" onClick={onCheckout}>Перейти к оплате <ChevronRight size={18}/></button>
      </>}
    </main>
  </>;
}

function EmptyCart() {
  return <div className="empty"><div className="empty-icon"><ShoppingBag/></div><h2>Корзина пуста</h2><p>Добавьте игру из каталога — она появится здесь.</p></div>;
}

function CheckoutPage({cart,total,onBack,onClear}) {
  const [busy,setBusy]=useState(false);
  const [result,setResult]=useState(null);
  async function pay() {
    setBusy(true);
    try {
      const user = tg?.initDataUnsafe?.user || demoUser;
      const order = await createOrder({telegram_user_id:String(user.id), items:cart.map(x=>({item_id:x.id,item_type:x.type||"game",quantity:x.quantity}))});
      setResult(order);
    } catch(e) {
      alert(e.message);
    } finally { setBusy(false); }
  }
  if (result) return <main className="content success-page"><div className="success-icon">✓</div><h1>Заказ создан</h1><p>Номер заказа <b>#{result.id}</b>. В этой MVP-версии реальная оплата ещё не подключена.</p><button className="primary wide" onClick={()=>{ if(tg?.openTelegramLink) tg.openTelegramLink(result.bot_url); else window.open(result.bot_url,"_blank"); }}>Перейти в бота</button><button className="ghost wide" onClick={onClear}>Вернуться в магазин</button></main>;
  return <>
    <Header title="Оплата" back onBack={onBack}/>
    <main className="content">
      <div className="checkout-total"><span>Сумма к оплате</span><strong>{money(total)}</strong></div>
      <div className="calc">
        <div><span>Товары</span><b>{cart.reduce((s,x)=>s+x.quantity,0)} шт.</b></div>
        <div><span>Валюта магазина</span><b>TRY</b></div>
        <div><span>Наценка</span><b>10%</b></div>
      </div>
      <div className="notice"><ShieldCheck/><span>После подтверждения оплаты заказ будет передан в Telegram-бот для оформления покупки.</span></div>
      <button className="primary wide" disabled={busy} onClick={pay}>{busy?"Создание заказа...":"Оплатить " + money(total)}</button>
      <p className="secure">🔒 Защищённая обработка заказа</p>
    </main>
  </>;
}

function ProfilePage({user}) {
  return <>
    <Header title="Профиль"/>
    <main className="content">
      <div className="profile-head"><div className="profile-avatar">{(user.first_name||"G").slice(0,1)}</div><div><h2>{user.first_name || "Пользователь"}</h2><span>@{user.username || "telegram"}</span></div></div>
      <div className="profile-menu">
        <button><ShoppingBag/><span>Мои заказы</span><ChevronRight/></button>
        <button><Sparkles/><span>Избранное</span><ChevronRight/></button>
        <button><ShieldCheck/><span>Поддержка</span><ChevronRight/></button>
        <button><Zap/><span>О приложении</span><ChevronRight/></button>
      </div>
      <div className="profile-banner"><Sparkles/><div><b>Больше игр. Впереди.</b><span>Покупайте любимые игры удобно.</span></div></div>
    </main>
  </>;
}

function BottomNav({page,setPage,cartCount}) {
  return <nav className="bottom-nav">
    <button className={page==="home"?"active":""} onClick={()=>setPage("home")}><Home/><span>Главная</span></button>
    <button className={page==="catalog"?"active":""} onClick={()=>setPage("catalog")}><LayoutGrid/><span>Каталог</span></button>
    <button className={page==="plus"?"active":""} onClick={()=>setPage("plus")}><Crown/><span>PS Plus</span></button>
    <button className={page==="cart"?"active":""} onClick={()=>setPage("cart")}><span className="nav-icon"><ShoppingBag/>{cartCount>0&&<i>{cartCount}</i>}</span><span>Корзина</span></button>
    <button className={page==="profile"?"active":""} onClick={()=>setPage("profile")}><UserRound/><span>Профиль</span></button>
  </nav>;
}

export default App;
