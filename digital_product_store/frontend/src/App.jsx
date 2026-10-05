import { useEffect, useState } from 'react'
import { Link, NavLink, Route, Routes, useNavigate, useSearchParams, useParams } from 'react-router-dom'
import toast from 'react-hot-toast'
import api from './api'

const money = n => `$${Number(n || 0).toFixed(2)}`

function Layout() {
  const [user, setUser] = useState(() => JSON.parse(localStorage.getItem('user') || 'null'))
  const nav = useNavigate()
  useEffect(() => {
    const handler = () => setUser(JSON.parse(localStorage.getItem('user') || 'null'))
    window.addEventListener('authchange', handler)
    return () => window.removeEventListener('authchange', handler)
  }, [])
  const logout = () => {
    localStorage.clear(); setUser(null); toast.success('Logged out'); nav('/products')
  }
  return <div className="min-h-screen">
    <header className="bg-slate-900 text-white">
      <div className="max-w-6xl mx-auto px-4 py-4 flex flex-wrap gap-4 items-center justify-between">
        <Link className="font-bold text-xl" to="/products">Digital Store</Link>
        <nav className="flex gap-3 items-center text-sm">
          <NavLink to="/products">Products</NavLink>
          {user && <NavLink to="/cart">Cart</NavLink>}
          {user && <NavLink to="/orders">Orders</NavLink>}
          {user?.role === 'admin' && <NavLink to="/admin/products">Admin</NavLink>}
          {user ? <button onClick={logout} className="bg-white text-slate-900 px-3 py-1 rounded">Logout</button>
                 : <><NavLink to="/login">Login</NavLink><NavLink to="/register">Register</NavLink></>}
        </nav>
      </div>
    </header>
    <main className="max-w-6xl mx-auto px-4 py-8"><Routes>
      <Route path="/" element={<Products/>}/>
      <Route path="/products" element={<Products/>}/>
      <Route path="/products/:id" element={<ProductDetail/>}/>
      <Route path="/login" element={<Login/>}/>
      <Route path="/register" element={<Register/>}/>
      <Route path="/cart" element={<RequireAuth><Cart/></RequireAuth>}/>
      <Route path="/orders" element={<RequireAuth><Orders/></RequireAuth>}/>
      <Route path="/admin/products" element={<RequireAdmin><AdminProducts/></RequireAdmin>}/>
      <Route path="/admin/orders" element={<RequireAdmin><AdminOrders/></RequireAdmin>}/>
    </Routes></main>
  </div>
}

function RequireAuth({children}) {
  return localStorage.getItem('token') ? children : <NavigateToLogin/>
}
function RequireAdmin({children}) {
  const u = JSON.parse(localStorage.getItem('user') || 'null')
  return u?.role === 'admin' ? children : <NavigateToLogin/>
}
function NavigateToLogin() { const nav = useNavigate(); useEffect(()=>nav('/login'),[]); return <p>Redirecting to login...</p> }

function Login() {
  const nav = useNavigate()
  const [form,setForm]=useState({email:'',password:''})
  const submit=async e=>{
    e.preventDefault()
    try {
      const r=await api.post('/auth/login',form)
      localStorage.setItem('token',r.data.access_token); localStorage.setItem('user',JSON.stringify(r.data.user))
      window.dispatchEvent(new Event('authchange')); toast.success('Login successful'); nav('/products')
    } catch(e){ toast.error(e.response?.data?.detail || 'Invalid credentials') }
  }
  return <FormCard title="Login"><form onSubmit={submit} className="space-y-4">
    <Input label="Email" type="email" value={form.email} onChange={e=>setForm({...form,email:e.target.value})}/>
    <Input label="Password" type="password" value={form.password} onChange={e=>setForm({...form,password:e.target.value})}/>
    <button className="btn bg-slate-900 text-white px-4 py-2 rounded-lg hover:bg-slate-700">Login</button>
  </form></FormCard>
}

function Register() {
  const nav=useNavigate()
  const [form,setForm]=useState({email:'',password:'',full_name:''})
  const submit=async e=>{
    e.preventDefault()
    try {
      const r=await api.post('/auth/register',form)
      localStorage.setItem('token',r.data.access_token); localStorage.setItem('user',JSON.stringify(r.data.user))
      window.dispatchEvent(new Event('authchange')); toast.success('Registration successful'); nav('/products')
    } catch(e){ toast.error(e.response?.data?.detail || 'Registration failed') }
  }
  return <FormCard title="Create account"><form onSubmit={submit} className="space-y-4">
    <Input label="Full name" value={form.full_name} onChange={e=>setForm({...form,full_name:e.target.value})}/>
    <Input label="Email" type="email" value={form.email} onChange={e=>setForm({...form,email:e.target.value})}/>
    <Input label="Password" type="password" value={form.password} onChange={e=>setForm({...form,password:e.target.value})}/>
    <button className="btn bg-slate-900 text-white px-4 py-2 rounded-lg hover:bg-slate-700">Register</button>
  </form></FormCard>
}

function FormCard({title,children}) { return <div className="max-w-md mx-auto bg-white p-6 rounded-xl shadow"><h1 className="text-2xl font-bold mb-5">{title}</h1>{children}</div> }
function Input({label,...props}) { return <label className="block text-sm font-medium">{label}<input {...props} required className="mt-1 w-full border rounded px-3 py-2"/></label> }

function Products() {
  const [data,setData]=useState({items:[],page:1,limit:6,total:0,total_pages:0})
  const [search,setSearch]=useState('')
  const [page,setPage]=useState(1)
  const load=async()=>{try{const r=await api.get(`/products?page=${page}&limit=6&search=${encodeURIComponent(search)}`);setData(r.data)}catch(e){toast.error('Unable to load products')}}
  useEffect(()=>{load()},[page,search])
  return <section>
    <div className="flex flex-wrap justify-between gap-3 mb-6"><div><h1 className="text-3xl font-bold">Digital Products</h1><p className="text-slate-500">Courses, guides and developer resources.</p></div>
      <input value={search} onChange={e=>{setPage(1);setSearch(e.target.value)}} placeholder="Search products..." className="border rounded px-3 py-2"/>
    </div>
    <div className="grid md:grid-cols-3 gap-5">
      {data.items.map(p=><div key={p.id} className="bg-white rounded-xl shadow overflow-hidden">
        <img src={p.image_url || 'https://placehold.co/600x400?text=Product'} className="w-full h-40 object-cover"/>
        <div className="p-4"><h2 className="font-bold text-lg">{p.name}</h2><p className="text-sm text-slate-500 h-10 overflow-hidden">{p.description}</p>
          <div className="flex justify-between items-center mt-4"><b>{money(p.price)}</b><Link className="btn bg-slate-900 text-white px-4 py-2 rounded-lg hover:bg-slate-700" to={`/products/${p.id}`}>View</Link></div>
        </div>
      </div>)}
    </div>
    <Pagination data={data} setPage={setPage}/>
  </section>
}

function Pagination({data,setPage}) {
  if (!data.total_pages) return <p className="mt-6 text-slate-500">No products found.</p>
  return <div className="flex justify-center gap-2 mt-8">
    <button className="pagebtn border px-3 py-1 rounded" disabled={data.page<=1} onClick={()=>setPage(data.page-1)}>Previous</button>
    {Array.from({length:data.total_pages},(_,i)=>i+1).slice(Math.max(0,data.page-3),data.page+2).map(n=><button key={n} onClick={()=>setPage(n)} className={`pagebtn ${n===data.page?'bg-slate-900 text-white':''}`}>{n}</button>)}
    <button className="pagebtn border px-3 py-1 rounded" disabled={data.page>=data.total_pages} onClick={()=>setPage(data.page+1)}>Next</button>
  </div>
}

function ProductDetail() {
  const {id}=useParams()
  const [p,setP]=useState(null)
  const [qty,setQty]=useState(1)
  useEffect(()=>{api.get(`/products/${id}`).then(r=>setP(r.data)).catch(()=>toast.error('Product not found'))},[id])
  if(!p) return <p>Loading...</p>
  const add=async()=>{if(!localStorage.getItem('token')){toast.error('Please login first');return}try{await api.post('/cart/items',{product_id:p.id,quantity:qty});toast.success('Product added to cart')}catch(e){toast.error(e.response?.data?.detail||'Something went wrong')}}
  return <div className="bg-white rounded-xl shadow p-6 grid md:grid-cols-2 gap-8">
    <img src={p.image_url || 'https://placehold.co/600x400?text=Product'} className="rounded-xl w-full"/>
    <div><h1 className="text-3xl font-bold">{p.name}</h1><p className="mt-4 text-slate-600">{p.description}</p><p className="text-2xl font-bold mt-6">{money(p.price)}</p>
    <div className="flex gap-3 mt-5"><input type="number" min="1" max="100" value={qty} onChange={e=>setQty(Math.max(1,Number(e.target.value)))} className="border rounded px-3 py-2 w-24"/><button onClick={add} className="btn bg-slate-900 text-white px-4 py-2 rounded-lg hover:bg-slate-700">Add to cart</button></div></div>
  </div>
}

function Cart() {
  const [cart,setCart]=useState({items:[],total_amount:0})
  const load=()=>api.get('/cart').then(r=>setCart(r.data)).catch(e=>toast.error(e.response?.data?.detail||'Could not load cart'))
  useEffect(load,[])
  const remove=async id=>{try{await api.delete(`/cart/items/${id}`);toast.success('Product removed');load()}catch(e){toast.error('Unable to remove')}}
  const checkout=async()=>{if(!cart.items.length){toast.error('Cart is empty');return}try{const r=await api.post('/payments/create-checkout-session');window.location.href=r.data.checkout_url}catch(e){toast.error(e.response?.data?.detail||'Payment failed')}}
  return <section><h1 className="text-3xl font-bold mb-5">Your Cart</h1><div className="bg-white rounded-xl shadow divide-y">
    {cart.items.map(i=><div key={i.id} className="p-4 flex justify-between items-center"><div><b>{i.product_name}</b><p>{i.quantity} × {money(i.unit_price)}</p></div><div className="flex gap-4 items-center"><b>{money(i.subtotal)}</b><button onClick={()=>remove(i.id)} className="text-red-600">Remove</button></div></div>)}
    {!cart.items.length&&<div className="p-8 text-center">Your cart is empty.</div>}
    <div className="p-5 flex justify-between font-bold text-xl"><span>Total</span><span>{money(cart.total_amount)}</span></div>
  </div>{cart.items.length>0&&<div className="text-right mt-5"><button onClick={checkout} className="btn bg-slate-900 text-white px-4 py-2 rounded-lg hover:bg-slate-700">Checkout with Stripe</button></div>}</section>
}

function Orders() {
  const [data,setData]=useState({items:[],page:1,limit:5,total:0,total_pages:0})
  const [params]=useSearchParams()
  const load=()=>api.get('/orders?page=1&limit=5').then(r=>setData(r.data))
  useEffect(()=>{load(); if(params.get('payment')==='success') toast.success('Payment completed; order status will update from Stripe webhook.')},[])
  return <section><h1 className="text-3xl font-bold mb-5">My Orders</h1>
    <div className="space-y-4">{data.items.map(o=><div key={o.id} className="bg-white rounded-xl shadow p-5"><div className="flex justify-between"><b>Order #{o.id}</b><span className="font-semibold">{o.status}</span></div><p className="text-sm text-slate-500">{new Date(o.created_at).toLocaleString()}</p><p className="mt-2">Payment: <b>{o.payment_status}</b> · Total: <b>{money(o.total_amount)}</b></p>
    <ul className="mt-3 text-sm">{o.items.map(i=><li key={i.product_id}>{i.product_name} × {i.quantity} — {money(i.subtotal)}</li>)}</ul></div>)}</div>
  </section>
}

function AdminProducts() {
  const blank={name:'',description:'',price:'',image_url:''}
  const [form,setForm]=useState(blank); const [products,setProducts]=useState([])
  const [editing,setEditing]=useState(null)
  const load=()=>api.get('/products?limit=100').then(r=>setProducts(r.data.items))
  useEffect(load,[])
  const create=async e=>{e.preventDefault();try{await api.post('/products',{...form,price:Number(form.price)});toast.success('Product created');setForm(blank);load()}catch(e){toast.error(e.response?.data?.detail||'Create failed')}}
  const saveEdit=async e=>{e.preventDefault();try{await api.put(`/products/${editing.id}`,{...form,price:Number(form.price)});toast.success('Product updated');setEditing(null);setForm(blank);load()}catch(e){toast.error(e.response?.data?.detail||'Update failed')}}
  const startEdit=p=>{setEditing(p);setForm({name:p.name,description:p.description,price:p.price,image_url:p.image_url||''})}
  const del=async id=>{try{await api.delete(`/products/${id}`);toast.success('Product deleted');load()}catch(e){toast.error('Delete failed')}}
  return <section><h1 className="text-3xl font-bold mb-5">Admin Products</h1><form onSubmit={editing?saveEdit:create} className="bg-white p-5 rounded-xl shadow mb-6 grid md:grid-cols-4 gap-3">
    <input className="border p-2 rounded" placeholder="Name" value={form.name} onChange={e=>setForm({...form,name:e.target.value})} required/>
    <input className="border p-2 rounded" placeholder="Description" value={form.description} onChange={e=>setForm({...form,description:e.target.value})}/>
    <input className="border p-2 rounded" placeholder="Price" type="number" step="0.01" value={form.price} onChange={e=>setForm({...form,price:e.target.value})} required/>
    <input className="border p-2 rounded" placeholder="Image URL" value={form.image_url} onChange={e=>setForm({...form,image_url:e.target.value})}/>
    <button className="btn md:col-span-4">{editing?'Update Product':'Create Product'}</button>
  </form>
  <div className="bg-white rounded-xl shadow divide-y">{products.map(p=><div key={p.id} className="p-4 flex justify-between items-center"><span><b>{p.name}</b> — {money(p.price)}</span><div className="flex gap-4"><button onClick={()=>startEdit(p)} className="text-blue-600">Edit</button><button onClick={()=>del(p.id)} className="text-red-600">Delete</button></div></div>)}</div>
  <Link className="inline-block mt-5 btn" to="/admin/orders">View Admin Orders & Stats</Link></section>
}

function AdminOrders() {
  const [stats,setStats]=useState(null); const [orders,setOrders]=useState([])
  useEffect(()=>{Promise.all([api.get('/admin/stats'),api.get('/admin/orders')]).then(([s,o])=>{setStats(s.data);setOrders(o.data.items)}).catch(e=>toast.error(e.response?.data?.detail||'Admin access failed'))},[])
  return <section><h1 className="text-3xl font-bold mb-5">Admin Dashboard</h1>
    {stats&&<div className="grid md:grid-cols-4 gap-4 mb-6">{[['Total Products',stats.total_products],['Total Orders',stats.total_orders],['Paid Orders',stats.paid_orders],['Revenue',money(stats.total_revenue)]].map(x=><div className="bg-white rounded-xl shadow p-5" key={x[0]}><p className="text-slate-500">{x[0]}</p><b className="text-2xl">{x[1]}</b></div>)}</div>}
    <div className="bg-white rounded-xl shadow divide-y">{orders.map(o=><div className="p-4 flex justify-between" key={o.id}><span>Order #{o.id}</span><span>{o.status} · {money(o.total_amount)}</span></div>)}</div>
  </section>
}

export default function App(){ return <Layout/> }
