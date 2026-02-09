"""
3D visualization and rendering for SPH simulation using PyVista
"""
import numpy as np
try:
    import pyvista as pv
    PYVISTA_AVAILABLE = True
except ImportError:
    PYVISTA_AVAILABLE = False
    print("Warning: PyVista not available. Visualization will be disabled.")


class SPHRenderer:
    """
    3D renderer for SPH fluid simulation using PyVista
    
    Provides real-time visualization of particles with various coloring options
    """
    
    def __init__(self, solver, window_size=(1920, 1080), off_screen=False):
        """
        Initialize renderer
        
        Args:
            solver: SPHSolver instance
            window_size: (width, height) of rendering window
            off_screen: If True, render off-screen (for video export)
        """
        if not PYVISTA_AVAILABLE:
            raise RuntimeError("PyVista is required for visualization. Install with: pip install pyvista")
        
        self.solver = solver
        self.plotter = pv.Plotter(window_size=window_size, off_screen=off_screen)
        
        # Configure plotter
        self.plotter.set_background('white')
        
        # Add domain boundary box
        self.add_domain_box()
        
        # Particle visualization
        self.particle_actor = None
        self.color_mode = 'default'
        
    def add_domain_box(self):
        """
        Add wireframe box showing simulation domain boundaries
        """
        bounds = [
            0, self.solver.domain_size[0],
            0, self.solver.domain_size[1],
            0, self.solver.domain_size[2]
        ]
        
        box = pv.Box(bounds=bounds)
        self.plotter.add_mesh(box, style='wireframe', color='gray', line_width=2, opacity=0.5)
    
    def update_particles(self, color_by='default', point_size=10, cmap='viridis'):
        """
        Update particle visualization
        
        Args:
            color_by: How to color particles
                     'default' - use particle colors
                     'velocity' - color by velocity magnitude
                     'pressure' - color by pressure
                     'density' - color by density
            point_size: Size of rendered points
            cmap: Matplotlib colormap name (for non-default coloring)
        """
        if self.solver.n_active == 0:
            return
        
        # Get particle positions
        positions = self.solver.particles.positions[:self.solver.n_active]
        
        # Create point cloud
        point_cloud = pv.PolyData(positions)
        
        # Determine coloring
        if color_by == 'velocity':
            velocities = self.solver.particles.velocities[:self.solver.n_active]
            colors = np.linalg.norm(velocities, axis=1)
            point_cloud['colors'] = colors
            use_cmap = True
        elif color_by == 'pressure':
            colors = self.solver.particles.pressures[:self.solver.n_active]
            point_cloud['colors'] = colors
            use_cmap = True
        elif color_by == 'density':
            colors = self.solver.particles.densities[:self.solver.n_active]
            point_cloud['colors'] = colors
            use_cmap = True
        else:
            # Use default particle colors
            colors = self.solver.particles.colors[:self.solver.n_active]
            point_cloud['colors'] = colors
            use_cmap = False
        
        # Remove previous particle actor
        if self.particle_actor is not None:
            self.plotter.remove_actor(self.particle_actor)
        
        # Add new particles
        if use_cmap:
            self.particle_actor = self.plotter.add_mesh(
                point_cloud,
                scalars='colors',
                render_points_as_spheres=True,
                point_size=point_size,
                cmap=cmap,
                show_scalar_bar=True
            )
        else:
            self.particle_actor = self.plotter.add_mesh(
                point_cloud,
                scalars='colors',
                rgb=True,
                render_points_as_spheres=True,
                point_size=point_size,
                show_scalar_bar=False
            )
        
        self.color_mode = color_by
    
    def render_frame(self, color_by=None):
        """
        Render a single frame
        
        Args:
            color_by: Optional color mode (uses previous if not specified)
        """
        if color_by is None:
            color_by = self.color_mode
        
        self.update_particles(color_by=color_by)
        self.plotter.render()
    
    def show_interactive(self):
        """
        Show interactive window
        
        User can rotate, zoom, and interact with the view
        """
        self.update_particles()
        self.plotter.show()
    
    def export_image(self, filename):
        """
        Export current frame as image
        
        Args:
            filename: Output filename (e.g., 'frame.png')
        """
        self.plotter.screenshot(filename)
    
    def add_text(self, text, position='upper_left', font_size=12, color='black'):
        """
        Add text overlay to the visualization
        
        Args:
            text: Text to display
            position: Position on screen ('upper_left', 'upper_right', etc.)
            font_size: Font size
            color: Text color
        """
        self.plotter.add_text(text, position=position, font_size=font_size, color=color)
    
    def set_camera(self, position=None, focal_point=None, viewup=None):
        """
        Set camera position and orientation
        
        Args:
            position: Camera position [x, y, z]
            focal_point: Point camera is looking at [x, y, z]
            viewup: Up direction [x, y, z]
        """
        if position is not None:
            self.plotter.camera_position = position
        if focal_point is not None:
            self.plotter.camera.focal_point = focal_point
        if viewup is not None:
            self.plotter.camera.up = viewup
    
    def close(self):
        """Close the plotter"""
        self.plotter.close()


class VideoExporter:
    """
    Export SPH simulation as video file
    """
    
    def __init__(self, solver, filename='output.mp4', fps=30, quality=5):
        """
        Initialize video exporter
        
        Args:
            solver: SPHSolver instance
            filename: Output video filename
            fps: Frames per second
            quality: Video quality (1-10, higher is better)
        """
        if not PYVISTA_AVAILABLE:
            raise RuntimeError("PyVista is required for video export")
        
        self.solver = solver
        self.filename = filename
        self.fps = fps
        self.quality = quality
        
        # Create off-screen renderer
        self.renderer = SPHRenderer(solver, window_size=(1920, 1080), off_screen=True)
    
    def export(self, duration, color_by='default', show_progress=True):
        """
        Run simulation and export to video
        
        Args:
            duration: Simulation duration in seconds
            color_by: Particle coloring mode
            show_progress: Show progress bar
        """
        n_frames = int(duration * self.fps)
        dt_per_frame = duration / n_frames
        steps_per_frame = max(1, int(dt_per_frame / self.solver.dt))
        
        # Open movie file
        self.renderer.plotter.open_movie(self.filename, framerate=self.fps, quality=self.quality)
        
        # Add info text
        self.renderer.add_text(
            f"SPH Fluid Simulation\n{self.solver.n_active} particles",
            position='upper_left',
            font_size=14
        )
        
        # Generate frames
        if show_progress:
            try:
                from tqdm import tqdm
                frame_iterator = tqdm(range(n_frames), desc="Rendering video")
            except ImportError:
                frame_iterator = range(n_frames)
                print(f"Rendering {n_frames} frames...")
        else:
            frame_iterator = range(n_frames)
        
        for frame in frame_iterator:
            # Simulate
            for _ in range(steps_per_frame):
                self.solver.step()
            
            # Render and write frame
            self.renderer.render_frame(color_by=color_by)
            self.renderer.plotter.write_frame()
            
            if not show_progress:
                if frame % 10 == 0:
                    print(f"Frame {frame+1}/{n_frames}")
        
        # Close video file
        self.renderer.plotter.close()
        
        if show_progress:
            print(f"\nVideo saved to: {self.filename}")
    
    def export_with_callback(self, duration, callback, color_by='default'):
        """
        Export video with custom callback for each frame
        
        Args:
            duration: Simulation duration in seconds
            callback: Function called each frame: callback(solver, frame_num, renderer)
            color_by: Particle coloring mode
        """
        n_frames = int(duration * self.fps)
        dt_per_frame = duration / n_frames
        steps_per_frame = max(1, int(dt_per_frame / self.solver.dt))
        
        self.renderer.plotter.open_movie(self.filename, framerate=self.fps, quality=self.quality)
        
        for frame in range(n_frames):
            # Simulate
            for _ in range(steps_per_frame):
                self.solver.step()
            
            # Custom callback
            if callback:
                callback(self.solver, frame, self.renderer)
            
            # Render and write
            self.renderer.render_frame(color_by=color_by)
            self.renderer.plotter.write_frame()
        
        self.renderer.plotter.close()
